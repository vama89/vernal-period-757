'use strict';

/**
 * @ngdoc object
 * @name conferenceApp
 * @requires $routeProvider
 * @requires conferenceControllers
 * @requires ui.bootstrap
 *
 * @description
 * Root app, which routes and specifies the partial html and controller depending on the url requested.
 *
 */
var app = angular.module('conferenceApp',
    ['conferenceControllers', 'ngRoute', 'ui.bootstrap', 'ngCookies']).
    config(['$routeProvider',
        function ($routeProvider) {
            $routeProvider.
                when('/myDashboard', {
                    templateUrl: '/partials/myDashboard.html',
                    controller: 'MyDashboardCtrl'
                }).
                when('/hangout/create', {
                    templateUrl: '/partials/createHangoutPort.html',
                    controller: 'HangoutCreationCtrl'
                }).
                when('/profile', {
                    templateUrl: '/partials/profile.html',
                    controller: 'MyProfileCtrl'
                }).
                when('/vote/:webSafeKey', {
                    templateUrl: '/partials/vote.html',
                    controller:'VoteCtrl'
                }).
                when('/results/:webSafeKey', {
                    templateUrl: '/partials/results.html',
                    controller:'ResultsCtrl'
                }).
                when('/waiting/:webSafeKey', {
                    templateUrl: '/partials/waiting.html',
                    controller:'ResultsCtrl'
                }).
                when('/test', {
                    templateUrl: '/partials/test.html',
                    controller: 'TestCtrl'
                }).
                    when('/invite', {
                    templateUrl: '/partials/invite.html',
                }).
                    when('/', {
                    templateUrl: '/partials/home.html',
                }).
                otherwise({
                    redirectTo: '/'
                });
        }]);

/**
 * @ngdoc filter
 * @name startFrom
 *
 * @description
 * A filter that extracts an array from the specific index.
 *
 */
app.filter('startFrom', function () {
    /**
     * Extracts an array from the specific index.
     *
     * @param {Array} data
     * @param {Integer} start
     * @returns {Array|*}
     */
    var filter = function (data, start) {
        return data.slice(start);
    }
    return filter;
});


/**
 * @ngdoc constant
 * @name HTTP_ERRORS
 *
 * @description
 * Holds the constants that represent HTTP error codes.
 *
 */
app.constant('HTTP_ERRORS', {
    'UNAUTHORIZED': 401
});


/**
 * @ngdoc service
 * @name oauth2Provider
 *
 * @description
 * Service that holds the OAuth2 information shared across all the pages.
 *
 */
app.factory('oauth2Provider', function ($modal) {
    var oauth2Provider = {
        CLIENT_ID: '1056255259427-h8spnd6q8ovv8cn6fdmqk6kc259mb6k6.apps.googleusercontent.com',
        SCOPES: 'email profile',
        signedIn: false
    }

    /**
     * Calls the OAuth2 authentication method.
     */
    oauth2Provider.signIn = function (callback) {
        gapi.auth.signIn({
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'accesstype': 'online',
            'approveprompt': 'auto',
            'scope': oauth2Provider.SCOPES,
            'callback': callback
        });
    };

    /**
     * Logs out the user.
     */
    oauth2Provider.signOut = function () {
        gapi.auth.signOut();
        // Explicitly set the invalid access token in order to make the API calls fail.
        gapi.auth.setToken({access_token: ''})
        oauth2Provider.signedIn = false;
    };

    /**
     * Shows the modal with Google+ sign in button.
     *
     * @returns {*|Window}
     */
    oauth2Provider.showLoginModal = function() {
        var modalInstance = $modal.open({
            templateUrl: '/partials/login.modal.html',
            controller: 'OAuth2LoginModalCtrl'
        });
        return modalInstance;
    };

    return oauth2Provider;
});
