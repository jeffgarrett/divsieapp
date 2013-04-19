var app = angular.module('divsie', ['ngResource', 'infinite-scroll']);

app.factory('Tasks', ['$resource', function($resource) {
    return $resource('api/v1/tasks/:id', {}, 
        { query: { method: 'GET', isArray: false } });
}]);

app.controller('TaskListCtrl', ['$scope', 'Tasks', function($scope, Tasks) {
    $scope.tasks = [];
    $scope.loading = false;
    $scope.extendList = function() {
        $scope.loading = true;
        var wrapper = Tasks.query({ offset: $scope.tasks.length }, function () {
            $scope.tasks = $scope.tasks.concat(wrapper.tasks);
            $scope.loading = false;
        },
        function() {
            $scope.loading = false;
        });
    };

    $scope.extendList();
}]);

app.controller('SettingsCtrl', ['$scope', function($scope) {
}]);

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
        when('/list', {templateUrl: 'fragments/task_list.html', controller: "TaskListCtrl"}).
        when('/settings', {templateUrl: 'fragments/settings.html', controller: "SettingsCtrl"}).
        otherwise({redirectTo: '/list'});
}]);
