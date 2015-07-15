'use strict';

/**
 * The root conferenceApp module.
 *
 * @type {conferenceApp|*|{}}
 */
var conferenceApp = conferenceApp || {};

/**
 * @ngdoc module
 * @name conferenceControllers
 *
 * @description
 * Angular module for controllers.
 *
 */
conferenceApp.controllers = angular.module('conferenceControllers', ['ui.bootstrap']);

/**
 * @ngdoc controller
 * @name MyProfileCtrl
 *
 * @description
 * A controller used for the My Profile page.
 */
conferenceApp.controllers.controller('MyProfileCtrl',
    function ($scope, $log, oauth2Provider, HTTP_ERRORS) {
        $scope.submitted = false;
        $scope.loading = false;

        /**
         * The initial profile retrieved from the server to know the dirty state.
         * @type {{}}
         */
        $scope.initialProfile = {};

        /**
         * Initializes the My profile page.
         * Update the profile if the user's profile has been stored.
         */
        $scope.init = function () {
            var retrieveProfileCallback = function () {
                $scope.profile = {};
                $scope.loading = true;
                gapi.client.conference.getProfile().
                    execute(function (resp) {
                        $scope.$apply(function () {
                            $scope.loading = false;
                            if (resp.error) {
                                // Failed to get a user profile.
                            } else {
                                // Succeeded to get the user profile.
                                $scope.profile.displayName = resp.result.displayName;
                                $scope.initialProfile = resp.result;
                            }
                        });
                    }
                );
            };
            if (!oauth2Provider.signedIn) {
                var modalInstance = oauth2Provider.showLoginModal();
                modalInstance.result.then(retrieveProfileCallback);
            } else {
                retrieveProfileCallback();
            }
        };

        /**
         * Invokes the conference.saveProfile API.
         *
         */
        $scope.saveProfile = function () {
            $scope.submitted = true;
            $scope.loading = true;
            gapi.client.conference.saveProfile($scope.profile).
                execute(function (resp) {
                    $scope.$apply(function () {
                        $scope.loading = false;
                        if (resp.error) {
                            // The request has failed.
                            var errorMessage = resp.error.message || '';
                            $scope.messages = 'Failed to update a profile : ' + errorMessage;
                            $scope.alertStatus = 'warning';
                            $log.error($scope.messages + 'Profile : ' + JSON.stringify($scope.profile));

                            if (resp.code && resp.code == HTTP_ERRORS.UNAUTHORIZED) {
                                oauth2Provider.showLoginModal();
                                return;
                            }
                        } else {
                            // The request has succeeded.
                            $scope.messages = 'The profile has been updated';
                            $scope.alertStatus = 'success';
                            $scope.submitted = false;
                            $scope.initialProfile = {
                                displayName: $scope.profile.displayName
                            };

                            $log.info($scope.messages + JSON.stringify(resp.result));
                        }
                    });
                });
        };

        $scope.pictureUpload = function(){
            //Hit the api
            //go into python
            //
        };

    });

/**
 * @ngdoc controller
 * @name RootCtrl
 *
 * @description
 * The root controller having a scope of the body element and methods used in the application wide
 * such as user authentications.
 *
 */
conferenceApp.controllers.controller('RootCtrl', function ($scope, $location, oauth2Provider) {

    /**
     * Returns if the viewLocation is the currently viewed page.
     *
     * @param viewLocation
     * @returns {boolean} true if viewLocation is the currently viewed page. Returns false otherwise.
     */
    $scope.isActive = function (viewLocation) {
        return viewLocation === $location.path();
    };

    /**
     * Returns the OAuth2 signedIn state.
     *
     * @returns {oauth2Provider.signedIn|*} true if siendIn, false otherwise.
     */
    $scope.getSignedInState = function () {
        return oauth2Provider.signedIn;
    };

    /**
     * Calls the OAuth2 authentication method.
     */
    $scope.signIn = function () {
        oauth2Provider.signIn(function () {
            gapi.client.oauth2.userinfo.get().execute(function (resp) {
                $scope.$apply(function () {
                    if (resp.email) {
                        oauth2Provider.signedIn = true;
                        $scope.alertStatus = 'success';
                        $scope.rootMessages = 'Logged in with ' + resp.email;
                    }
                });
            });
        });
    };

    /**
     * Render the signInButton and restore the credential if it's stored in the cookie.
     * (Just calling this to restore the credential from the stored cookie. So hiding the signInButton immediately
     *  after the rendering)
     */
    $scope.initSignInButton = function () {
        gapi.signin.render('signInButton', {
            'callback': function () {
                jQuery('#signInButton button').attr('disabled', 'true').css('cursor', 'default');
                if (gapi.auth.getToken() && gapi.auth.getToken().access_token) {
                    $scope.$apply(function () {
                        oauth2Provider.signedIn = true;
                    });
                }
            },
            'clientid': oauth2Provider.CLIENT_ID,
            'cookiepolicy': 'single_host_origin',
            'scope': oauth2Provider.SCOPES
        });
    };

    /**
     * Logs out the user.
     */
    $scope.signOut = function () {
        oauth2Provider.signOut();
        $scope.alertStatus = 'success';
        $scope.rootMessages = 'Logged out';
    };

    /**
     * Collapses the navbar on mobile devices.
     */
    $scope.collapseNavbar = function () {
        angular.element(document.querySelector('.navbar-collapse')).removeClass('in');
    };

});

/**
 * @ngdoc controller
 * @name OAuth2LoginModalCtrl
 *
 * @description
 * The controller for the modal dialog that is shown when an user needs to login to achive some functions.
 *
 */
conferenceApp.controllers.controller('OAuth2LoginModalCtrl',
    function ($scope, $modalInstance, $rootScope, oauth2Provider) {
        $scope.singInViaModal = function () {
            oauth2Provider.signIn(function () {
                gapi.client.oauth2.userinfo.get().execute(function (resp) {
                    $scope.$root.$apply(function () {
                        oauth2Provider.signedIn = true;
                        $scope.$root.alertStatus = 'success';
                        $scope.$root.rootMessages = 'Logged in with ' + resp.email;
                    });

                    $modalInstance.close();
                });
            });
        };
    });

/**
 * Method to show certain hangouts
 *
 */
conferenceApp.controllers.controller('HangoutCreationCtrl', function ($scope, $log){

    $scope.checked = $scope.checked || {};

    $scope.friendButton = function(hangoutForm) {
        $(document).ready(function() {
        var iCnt = 0;
        // CREATE A "DIV" ELEMENT AND DESIGN IT USING JQUERY ".css()" CLASS.
        var container = $(document.createElement('div')).css({
            padding: '5px', margin: '20px', width: '170px',
            borderTopColor: '#999', borderBottomColor: '#999',
            borderLeftColor: '#999', borderRightColor: '#999'
        });
        $('#btAdd').click(function() {
            if (iCnt <= 50) {
                iCnt = iCnt + 1;
                // ADD TEXTBOX.
                $(container).prepend('<input type=text class="input" id=tb' + iCnt + ' ' +
                            'ng-model="checked.friend' + iCnt + '" placeholder="Friend ' + iCnt +'"'+'required/>');

                if (iCnt == 100) {        // SHOW SUBMIT BUTTON IF ATLEAST "1" ELEMENT HAS BEEN CREATED.
                    var divSubmit = $(document.createElement('div'));
                    $(divSubmit).append('<input type=button class="bt" onclick="GetTextValue()"' + 
                            'id=btSubmit value=Submit />');   
                }
                $('#main').after(container, divSubmit);   // ADD BOTH THE DIV ELEMENTS TO THE "main" CONTAINER.
            }
            else {      // AFTER REACHING THE SPECIFIED LIMIT, DISABLE THE "ADD" BUTTON. (20 IS THE LIMIT WE HAVE SET)
                $(container).append('<label>Reached the limit</label>'); 
                $('#btAdd').attr('class', 'bt-disable'); 
                $('#btAdd').attr('disabled', 'disabled');
            }
        });
        $('#btRemove').click(function() {   // REMOVE ELEMENTS ONE PER CLICK.
            if (iCnt != 0) { $('#tb' + iCnt).remove(); iCnt = iCnt - 1; }
            if (iCnt == 0) { $(container).empty(); 
                $(container).remove(); 
                $('#btSubmit').remove(); 
                $('#btAdd').removeAttr('disabled'); 
                $('#btAdd').attr('class', 'bt') 
            }
        });
        $('#btRemoveAll').click(function() {    // REMOVE ALL THE ELEMENTS IN THE CONTAINER.
            $(container).empty(); 
            $(container).remove(); 
            $('#btSubmit').remove(); iCnt = 0; 
            $('#btAdd').removeAttr('disabled'); 
            $('#btAdd').attr('class', 'bt');
        });
    });

    // PICK THE VALUES FROM EACH TEXTBOX WHEN "SUBMIT" BUTTON IS CLICKED.
    //var divValue, values = '';
    //function GetTextValue() {
    //    $(divValue).empty(); 
    //    $(divValue).remove(); values = '';
    //    $('.input').each(function() {
    //        divValue = $(document.createElement('div')).css({
    //            padding:'5px', width:'200px'
    //        });
    //        values += this.value + '<br />'
    //    });
    //    $(divValue).append('<p><b>Your selected values</b></p>' + values);
    //    $('body').append(divValue);
    //}
    };

    $scope.allOptionsChecked = function(hangoutForm) {
        if ($scope.checked.location && $scope.checked.time && $scope.checked.day) {
            return true;
        }
        return false;
    };

    $scope.locationTime = function(hangoutForm) {
        if ($scope.checked.location && $scope.checked.time && !$scope.checked.day) {
            return true;
        }
        return false;
    };

    $scope.locationDay = function(hangoutForm) {
        if ($scope.checked.location && $scope.checked.day && !$scope.checked.time) {
            return true;
        }
        return false;

    };

    $scope.timeDay = function(hangoutForm) {
        if ($scope.checked.time && $scope.checked.day && !$scope.checked.location){
            return true;
        }
        return false;
    };

    $scope.time = function(hangoutForm) {
        if ($scope.checked.time && !$scope.checked.day && !$scope.checked.location){
            return true;
        }
        return false;
    };
    
    $scope.day = function(hangoutForm) {
       if ($scope.checked.day && !$scope.checked.time && !$scope.checked.location){
        return true;
       }
       return false;
    };
    
    $scope.location = function(hangoutForm) {
       if ($scope.checked.location && !$scope.checked.day && !$scope.checked.time){
        return true;
       }
       return false;
    };

    $scope.createHangout = function (hangoutForm) {
        //Grab all the individual friends and put them into a list
        //Seems I need these entities as strings in order for it to work with the python model
        var friendList = [$scope.checked.friend1, $scope.checked.friend2, $scope.checked.friend3];
        $scope.checked.friendList = JSON.stringify(friendList);
        
        var userVote = [$scope.checked.option1, $scope.checked.option2, $scope.checked.option3];
        //Convert to integers
        var i;
        for(i=0; i<3; i++){
            userVote[i]=parseInt(userVote[0]);
        };
        $scope.checked.groupVoteRanks = JSON.stringify(userVote);

        gapi.client.conference.createHangout($scope.checked).
            execute(function(resp){
                $scope.$apply(function() {
                    if (resp.error){
                        $log.error('There was an Error Yo');
                    }
                    else {
                        $log.info("Success Bitch!");
                        $log.info(resp);
                        $log.info(resp.result);
                    }
                });
            });
    };

});

conferenceApp.controllers.controller('MyDashboardCtrl', function($scope,$log){
    $scope.stillVoting = function(){
        //Ping the database to see if vote is true or false
        //return True if they are still voting



    };

    $scope.invited = function () {
        //Check if in the backend he was invited and didn't vote
        /*
        if he was invited return Events
            Under true, showcase the resp of the gapi
        else return false
        */

    };

    $scope.votedWaiting = function () {
        //Check if he voted and is waiting on the event
        /*
        if he was VotedandisWaiting return Events
            Under true, showcase the resp of the gapi
        else return false
        */

        gapi.client.conference.votedWaiting().
            execute(function(resp){
                $scope.$apply(function() {
                    if (resp.error){
                        $log.error('There was an Error Yo');
                    }
                    else {
                        $log.info("Success Bitch!");
                        $scope.hangouts = []
                        $scope.hangout=[]
                        angular.forEach(resp.items, function(hangout){
                            $scope.hangouts.push(hangout);
                        });
                    }
                });
            });
    };

    $scope.done = function () {
        /*
        if he was invited return Events
            Under true, showcase the resp of the gapi
        else return false
        */

    };


});

conferenceApp.controllers.controller('RegLogsCtrl', function($scope,$log){
    /*
    Get the models for registration

    send through the api and see if it has been created. if not send a reply
    back that user already exists and try another login.
    */

    //Set the global variable
    $scope.regLogInfo = $scope.regLogInfo || {};

    $scope.emailRegistration = function(registrationForm){

        $log.info($scope.regLogInfo);

    };

});

conferenceApp.controllers.controller('VoteCtrl', function($scope){

});

conferenceApp.controllers.controller('ResultsCtrl', function($scope){

});

conferenceApp.controllers.controller('ShowAllCtrl', function($scope, $log) {
 
    $scope.getAllHangouts = function() {
            gapi.client.conference.getAllHangouts().
                execute(function (resp) {
                    $scope.$apply(function(){
                        if(resp.error) {
                            $scope.message = 'Error Boss';
                            $log.error($scope.message);

                        } else {
                            $scope.message = 'Success Boss';
                            $log.info($scope.message);
                        }
                    });

                });
        };
});
