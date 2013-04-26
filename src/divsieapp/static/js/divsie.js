var app = angular.module('divsie', ['ngResource', 'infinite-scroll']);

app.factory('$localStorage', ['$window', function($window) {
    var prefix = '';
    var available = ('localStorage' in $window && $window.localStorage !== null);
    var emptyFn = function() { return null; };
    var version = emptyFn, setItem = emptyFn, getItem = emptyFn, removeItem = emptyFn, clear = emptyFn;

    if (available) {
        var storage = $window.localStorage;

        version = function(a, v) {
            var app = a + '|';
            prefix = app + v + '|';

            var oldKeys = [];
            for (var i = 0; i < storage.length; i++)
            {
                var key = storage.key(i);
                if (key.indexOf(app) == 0) {
                    if (key.indexOf(prefix) != 0) {
                        oldKeys.push(key);
                    }
                }
            }

            for (var i = 0; i < oldKeys.length; i++)
            {
                storage.removeItem(oldKeys[i]);
            }
        };

        setItem = function(key, val) {
            storage.setItem(prefix + key, JSON.stringify(val));
        };

        getItem = function(key) {
            return JSON.parse(storage.getItem(prefix + key));
        };

        removeItem = function(key) {
            storage.removeItem(prefix + key);
        };

        clear = function() {
            var keys = [];
            for (var i = 0; i < storage.length; i++)
            {
                var key = storage.key(i);
                if (key.indexOf(prefix) == 0) {
                    keys.push(key);
                }
            }

            for (var i = 0; i < keys.length; i++)
            {
                storage.removeItem(keys[i]);
            }
        };
    }

    return {
        'version': version,
        'setItem': setItem,
        'getItem': getItem,
        'removeItem': removeItem,
        'clear': clear
    };
}]);

app.factory('Tasks', ['$resource', '$localStorage', function($resource, $localStorage) {
    var Task = $resource('api/v1/tasks/:id', { id: '@id' },
        { query: { method: 'GET', isArray: false } });

    Task.prototype._save = Task.prototype.$save;
    Task.prototype.$save = function(success, error) {
        $localStorage.setItem('task:' + this.id, this);
        this._save(success, error);
    };

    Task.prototype.$complete = function(success, error) {
        if (!this.completed) {
            this.completed = true;
            this.completion_time = new Date();
            this.$save(success, error);
        }
    };

    return Task;
}]);

app.factory('Search', ['$rootScope', '$timeout', '$localStorage', function($rootScope, $timeout, $localStorage) {
    var timer, searches;

    var search = function(name, text) {
        if (text === undefined) {
            return;
        }

        if (timer !== undefined) {
            $timeout.cancel(timer);
        }

        timer = $timeout(function() {
            searches[name] = text;
            $localStorage.setItem('Search', searches);
            $rootScope.$broadcast('search', { name: name, text: text });
        }, 200);
    };

    var get = function(name) {
        return searches[name];
    }

    var on = function(name, callback) {
        $rootScope.$on('search', function(evt, args) {
            if (args.name == name) {
                callback(args.text);
            }
        });

        // Trigger event for late binders
        var lastSearch = searches[name];
        if (lastSearch !== undefined && lastSearch !== '') {
            search(name, lastSearch);
        }
    };

    // Initialization
    searches = $localStorage.getItem('Search');
    if (searches === undefined) {
        searches = {};
        $localStorage.setItem('Search', searches);
    }

    return {
        search: search,
        get: get,
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
            scope.text = Search.get(scope.name);
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
    $scope._tasks = [];
    $scope.tasks = [];
    $scope.offset = 0;
    $scope.more = true;
    $scope.task_filter = '';

    var filterTasks = function(tasks) {
        var r = [];
        var f = $scope.task_filter.toLowerCase();
        for (var i = 0; i < tasks.length; i++) {
            var t = tasks[i].title.toLowerCase();

            if (t.indexOf(f) != -1) {
                r.push(tasks[i]);
            }
        }
        return r;
    };

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
        var wrapper = Tasks.query({ offset: $scope.offset }, function () {
            if (clearTasks) {
                $scope._tasks = [];
                $scope.tasks = [];
            }
            angular.forEach(wrapper.tasks, function(m) { $scope._tasks.push(new Tasks(m)); });
            $scope.offset = wrapper.offset;
            $scope.more = wrapper.more;
            $scope.loading = false;
            $scope.tasks = filterTasks($scope._tasks);
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

        filter_timeout = $timeout(function() {
            //$scope.extendList(true);
            $scope.tasks = filterTasks($scope._tasks);
        }, 500);
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

app.run(['$rootScope', '$localStorage', function($rootScope, $localStorage) {
    $localStorage.version('divsie', 'v1');
    $rootScope.$on('$routeChangeSuccess', function (event, current, previous) {
        $rootScope.title = current.title;
    });
}]);
