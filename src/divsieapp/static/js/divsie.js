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

app.controller('TaskListCtrl', ['$scope', '$timeout', 'Tasks', function($scope, $timeout, Tasks) {
    $scope.tasks = [];
    $scope.offset = 0;
    $scope.more = true;
    $scope.task_filter = '';

    $scope.loading = false;
    $scope.extendList = function(clearTasks) {
        if ($scope.loading) {
            return;
        }
        if (!$scope.more && !clearTasks) {
            return;
        }
        $scope.loading = true;
        if (clearTasks) {
            $scope.offset = 0;
        }
        var wrapper = Tasks.query({ filter: $scope.task_filter, offset: $scope.offset }, function () {
            if (clearTasks) {
                $scope.tasks = [];
            }
            angular.forEach(wrapper.tasks, function(m) { $scope.tasks.push(new Tasks(m)); });
            $scope.offset = wrapper.offset;
            $scope.more = wrapper.more;
            $scope.loading = false;
        },
        function() {
            $scope.loading = false;
        });
    };
    //$scope.extendList();

    var filter_timeout;
    $scope.switchFilter = function(newValue) {
        // Wait for a break in typing
        if (filter_timeout) {
            $timeout.cancel(filter_timeout);
        }

        filter_timeout = $timeout(function() { $scope.extendList(true); }, 500);
    };
    $scope.$watch('task_filter', $scope.switchFilter);
}]);

app.controller('TaskNowCtrl', ['$scope', 'Tasks', function($scope, Tasks) {
    $scope.tasks = [];

    $scope.refresh = function() {
        var wrapper = Tasks.query({ current: true }, function () {
            angular.forEach(wrapper.tasks, function(m) { $scope.tasks.push(new Tasks(m)); });
            /* $scope.tasks = $scope.tasks.concat(wrapper.tasks); */
            $scope.loading = false;
        });
    };

    $scope.refresh();
}]);

app.controller('SettingsCtrl', ['$scope', '$rootScope', 'Tasks', function($scope, $rootScope, Tasks) {
    $rootScope.page_title = 'Settings';

    $scope.deleteTasks = function() {
        Tasks.delete();
    };
}]);

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/list', { templateUrl: 'fragments/task_list.html', controller: 'TaskListCtrl' })
        .when('/now', { templateUrl: 'fragments/task_now.html', controller: 'TaskNowCtrl' })
        .when('/settings', { templateUrl: 'fragments/settings.html', controller: 'SettingsCtrl' })
        .otherwise({ redirectTo: '/list' });
}]);
