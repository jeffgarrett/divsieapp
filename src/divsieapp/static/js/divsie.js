var app = angular.module('divsie', ['ngResource', 'ui.bootstrap', 'infinite-scroll']);

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

    Task.prototype.$start = function(success, error) {
        this.active = true;
        this.$save(success, error);
    };

    Task.prototype.$complete = function(success, error) {
        if (!this.completed) {
            this.completed = true;
            this.completion_time = new Date();
            this.$save(success, error);
        }
    };

    Task.prototype.$parse = function(s) {
        var lines = s.split('\n');
        var tags = [];

        for (var i = lines.length-1; i >= 0; i--)
        {
            if (lines[i] == '') {
                lines.pop();
                continue;
            }

            var regular_line = false;
            var line_tags = [];
            var words = lines[i].split(' ');
            for (var j = 0; j < words.length; j++)
            {
                if (words[j] == '') {
                    continue;
                }
                if (words[j].charAt(0) != '#') {
                    regular_line = true;
                    break;
                }
                line_tags.push(words[j].slice(1));
            }

            if (regular_line) {
                break;
            }

            lines.pop();

            for (var k = 0; k < line_tags.length; k++) {
                tags.push(line_tags[k]);
            }
        }

        this.content = lines.join('\n');
        this.tags = tags;
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

        //timer = $timeout(function() {
            searches[name] = text;
            $localStorage.setItem('Search', searches);
            $rootScope.$broadcast('search', { name: name, text: text });
        //}, 200);
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
    if (searches === null) {
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
        template: '<span class="input-append"><input type="search" placeholder="{{placeholder}}" ng-model="text"><i class="add-on icon-remove"></i><i class="add-on icon-search"></i></span>',
        replace: true,
        link: function(scope, element, attrs) {
            var removeIcon = false;

            scope.text = Search.get(scope.name);
            scope.$watch('text', function(text) {
                if (removeIcon && text == '') {
                    removeIcon = false;
                    element.children('.icon-remove').css('visibility', 'hidden');
                }
                else if (!removeIcon && text != '') {
                    removeIcon = true;
                    element.children('.icon-remove').css('visibility', 'visible');
                }
                Search.search(scope.name, text);
            });
            Search.on('navsearch', function(newValue) {
                scope.text = newValue;
            });
            element.on('focusin', function() {
                // expand
                //element.children('input').animate({ 'width': '400px' }, 500);
            });
            element.on('focusout', function() {
                // contract
                //element.children('input').animate({ 'width': '200px' }, 500);
            });
            element.children('.icon-remove').on('click', function() {
                scope.$apply(function() {
                    scope.text = '';
                });
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
app.directive('dvTaskCard', ['Search', '$timeout', function(Search, $timeout) {
    return {
        restrict: 'E',
        scope: {
            task: '=task',
        },
        templateUrl: '/fragments/task_card.html',
        replace: true,
        link: function(scope, element, attrs) {
            var tags = [];
            angular.forEach(scope.task.tags, function(tag) {
                this.push('#' + tag);
            }, tags);
            scope.setEditText = function() {
                scope.editText = scope.task.content;
                if (tags) {
                    scope.editText += '\n' + tags.join(' ');
                }
            };
            scope.setEditText();

            scope.$watch('editText', function(editText) {
                var area = element.children('.card-edit');
                area.css('height', 'auto');
                area.css('height', area[0].scrollHeight + 'px');
            });
            scope.start = function(task) {
                task.$start();
            };
            scope.edit = function(task) {
                scope.setEditText();
                element.addClass('edit');
                element.children('.card-noedit').hide();
                element.children('.card-edit').show();
                var area = element.children('.card-edit');
                area.css('height', 'auto');
                area.css('height', area[0].scrollHeight + 'px');
                area[0].focus();
                area[0].setSelectionRange(task.content.length, task.content.length);
            };
            scope.complete = function(task) {
                element.animate({ opacity: 0.5 }, 400, function() {
                    $(this).animate({ left: "150%" }, 600, function() {
                        $(this).hide();
                    });
                });

                //elem.addClass("completed");
                //$timeout(function() { elem.left = "150%"; }, 250);
                task.$complete();
            };
            scope.searchTag = function(tag, $event) {
                Search.search('navsearch', '#' + tag);
                $event.stopPropagation();
            };
            element.children('.card-noedit').bind('click', function() {
                scope.edit(scope.task);
            });
            element.children('.card-edit').bind('blur', function() {
                scope.$apply(function() {
                    element.removeClass('edit');
                    element.children('.card-edit').hide();
                    element.children('.card-noedit').show();
                    scope.statusText = 'Saving...'

                    scope.task.$parse(scope.editText);
                    scope.task.$save(function() {
                        scope.statusText = 'Saved';
                        $timeout(function() {
                            scope.statusText = '';
                        }, 500);
                    });
                });
            });
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
        var r = tasks.slice(0);
        var tokens = $scope.task_filter.split(' ');

        for (var i = 0; i < tokens.length; i++)
        {
            var t = tokens[i].toLowerCase();
            t = t.replace(/[\.,-\/#!$%\^&\*;:{}=\-_`~()]/g,"");

            if (t === '') {
                continue;
            }

            for (var j = 0; j < r.length; j++)
            {
                // Match the token against the content
                var content = r[j].content.toLowerCase();
                content = content.replace(/[\.,-\/#!$%\^&\*;:{}=\-_`~()]/g,"")
                if (content.indexOf(t) !== -1) {
                    continue;
                }

                // Or match the token against the tags
                var match = false;
                if (t.charAt(0) === '#') {
                    t = t.slice(1);
                }
                for (var k = 0; k < r[j].tags.length; k++)
                {
                    var tag = r[j].tags[k].toLowerCase();
                    if (tag.indexOf(t) !== -1) {
                        match = true;
                        break;
                    }
                }

                if (match) {
                    continue;
                }

                r = r.slice(0,j).concat(r.slice(j+1));
                j = j-1;
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
            //$timeout.cancel(filter_timeout);
        }

        //filter_timeout = $timeout(function() {
            //$scope.extendList(true);
            $scope.tasks = filterTasks($scope._tasks);
        //}, 500);
    };

    Search.on('navsearch', $scope.switchFilter);
}]);

app.controller('TaskNowCtrl', ['$scope', 'Tasks', function($scope, Tasks) {
    $scope.tasks = [];

    $scope.refresh = function() {
        var wrapper = Tasks.query({ active: true }, function () {
            angular.forEach(wrapper.tasks, function(m) { $scope.tasks.push(new Tasks(m)); });
            /* $scope.tasks = $scope.tasks.concat(wrapper.tasks); */
            $scope.loading = false;
        });
    };

    $scope.refresh();
}]);

app.controller('SettingsCtrl', ['$scope', '$dialog', 'Tasks', function($scope, $dialog, Tasks) {
    $scope.deleteTasks = function() {
        var title = 'Delete all tasks';
        var msg = 'This cannot be undone. Are you sure you want to delete all tasks?';
        var btns = [{ result: 'cancel', label: 'Cancel'}, { result: 'delete', label: 'Delete', cssClass: 'btn-danger' }];

        $dialog.messageBox(title, msg, btns).open()
            .then(function(result) {
                if (result == 'delete') {
                    Tasks.delete();
                }
            });
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
