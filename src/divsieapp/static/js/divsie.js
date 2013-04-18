var app = angular.module('divsie', ['ngResource']);

app.factory('Tasks', ['$resource', function($resource) {
    return $resource('api/v1/tasks/:id', {}, 
        { query: { method: 'GET', isArray: false } });
}]);

app.controller('TaskListCtrl', ['$scope', 'Tasks', function($scope, Tasks) {
    $scope.tasks = [];
    var wrapper = Tasks.query(function () {
        $scope.tasks = wrapper.tasks;
    });
}]);

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider.
        when('/list', {templateUrl: 'fragments/task_list.html', controller: "TaskListCtrl"}).
        otherwise({redirectTo: '/list'});
}]);
