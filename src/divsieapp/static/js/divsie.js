var app = angular.module('divsie', ['ngResource', 'infinite-scroll']);

app.factory('Tasks', ['$resource', function($resource) {
    var Task = $resource('api/v1/tasks/:id', { id: '@id' },
        { query: { method: 'GET', isArray: false } });

    Task.prototype.$complete = function(success, error) {
        if (!this.completed) {
            this.completed = true;
            this.completion_time = new Date();
            this.$save(success, error);
        }
    };

    return Task;
}]);

app.controller('TaskListCtrl', ['$scope', 'Tasks', function($scope, Tasks) {
    $scope.tasks = [];
    $scope.loading = false;
    $scope.extendList = function() {
        $scope.loading = true;
        var wrapper = Tasks.query({ offset: $scope.tasks.length }, function () {
            angular.forEach(wrapper.tasks, function(m) { $scope.tasks.push(new Tasks(m)); });
            /* $scope.tasks = $scope.tasks.concat(wrapper.tasks); */
            $scope.loading = false;
        },
        function() {
            $scope.loading = false;
        });
    };

    $scope.extendList();
}]);

app.controller('SettingsCtrl', ['$scope', 'Tasks', function($scope, Tasks) {
    $scope.deleteTasks = function() {
        Tasks.delete();
    };
}]);

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
        when('/list', {templateUrl: 'fragments/task_list.html', controller: "TaskListCtrl"}).
        when('/settings', {templateUrl: 'fragments/settings.html', controller: "SettingsCtrl"}).
        otherwise({redirectTo: '/list'});
}]);
