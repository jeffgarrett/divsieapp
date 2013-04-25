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

app.factory('Search', ['$rootScope', '$timeout', function($rootScope, $timeout) {
    var timer;

    var search = function(name, text) {
        if (text === undefined) {
            return;
        }

        if (timer !== undefined) {
            $timeout.cancel(timer);
        }

        timer = $timeout(function() {
            $rootScope.$broadcast('search', { name: name, text: text });
        }, 200);
    };

    var on = function(name, callback) {
        $rootScope.$on('search', function(evt, args) {
            if (args.name == name) {
                callback(args.text);
            }
        });
    };

    return {
        search: search,
        on: on
    };
}]);

app.directive('search', ['Search', function(Search) {
    return {
        restrict: 'E',
        scope: {
            placeholder: '@',
            name: '@'
        },
        template: '<span class="input-append"><input type="search" placeholder="{{placeholder}}" ng-model="text"><i class="add-on icon-search"></i></span>',
        replace: true,
        link: function(scope, element, attrs) {
            scope.$watch('text', function(text) {
                Search.search(scope.name, text);
            });
            element.on('focusin', function() {
                // expand
                // element.children().css('box-shadow', 'inset -1px 1px 1px rgba(0,0,0,0.075), 1px 0px 1px rgba(82,168,236,0.6)');
                element.children().css('box-shadow', 'none');
                element.children().css('border-color', 'rgba(82,168,236,0.8)');
                element.children('input').animate({ 'width': '400px' }, 500);
            });
            element.on('focusout', function() {
                // contract
                // element.children().css('box-shadow', 'inset -1px 1px 1px rgba(0,0,0,0.075)');
                element.children().css('box-shadow', 'none');
                element.children().css('border-color', '#ccc');
                element.children('input').animate({ 'width': '200px' }, 500);
            });
        }
    }
}]);

app.directive('file', function() {
    return {
        restrict: 'E',
        scope: {},
        template: '<span ng-transclude />',
        replace: true,
        transclude: true,
        require: 'ngModel',
        link: function(scope, element, attrs, ctrl) {
            // Hidden input element, behind a proxy element
            var fileInput = $('<input />')
                .attr('type', 'file')
                .on('change', function() {
                    scope.$apply(function() {
                        attr.multiple ? ctrl.$setViewValue(fileInput[0].files) : ctrl.$setViewValue(fileInput[0].files[0]);
                    });
                });

            element.on('click', function() {
                fileInput.click();
            });
        }
    }
});

// Requires jQuery for effects
app.directive('dvTaskCard', ['$timeout', function($timeout) {
    return {
        restrict: 'EA',
        scope: {
            task: '=task',
        },
        templateUrl: '/fragments/task_card.html',
        link: function(scope, elem, attr) {
            scope.complete = function(task) {
                elem.animate({ opacity: 0.5 }, 400, function() {
                    $(this).animate({ left: "150%" }, 600, function() {
                        $(this).hide();
                    });
                });

                //elem.addClass("completed");
                //$timeout(function() { elem.left = "150%"; }, 250);
                task.$complete();
            };
        }
    }
}]);

app.controller('TaskListCtrl', ['$scope', '$timeout', 'Tasks', 'Search', function($scope, $timeout, Tasks, Search) {
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
        $scope.task_filter = newValue;

        // Wait for a break in typing
        if (filter_timeout) {
            $timeout.cancel(filter_timeout);
        }

        filter_timeout = $timeout(function() { $scope.extendList(true); }, 500);
    };

    Search.on('navsearch', $scope.switchFilter);
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

app.controller('SettingsCtrl', ['$scope', 'Tasks', function($scope, Tasks) {
    $scope.deleteTasks = function() {
        Tasks.delete();
    };
}]);

app.config(['$routeProvider', function($routeProvider) {
    $routeProvider
        .when('/list', { templateUrl: 'fragments/task_list.html', title: 'Tasks', controller: 'TaskListCtrl' })
        .when('/now', { templateUrl: 'fragments/task_now.html', title: 'Now', controller: 'TaskNowCtrl' })
        .when('/settings', { templateUrl: 'fragments/settings.html', title: 'Settings', controller: 'SettingsCtrl' })
        .otherwise({ redirectTo: '/list' });

}]);

app.run(['$rootScope', function($rootScope) {
    $rootScope.$on('$routeChangeSuccess', function (event, current, previous) {
        if (current.$route) {
            $rootScope.title = current.$route.title;
        }
    });
}]);
