var Backbone = require('backbone');
var _ = require('underscore');
var $ = require('jquery');

var LoginView = Backbone.View.extend({
    template: _.template( require( './../templates/login-template' ) ),

    events: {
        'click .login-button': 'login',
        'click .register-button': 'register',
        'click .forgot-password': 'showPasswordReset',
        'keyup input': 'inputChanged',
    },

    login: function() {
        var email = this.emailInput.val();

        /*
         * If the password row isn't visible, it means we're in the process
         * of resetting a password and have submitted.
         * There's probably a better way to do this, but for the time being,
         * this is the way.
         */
        if ( ! this.passwordRow.is( ':visible' ) ) {
            this.submitPasswordReset( email );
            return;
        }
        if ( this.registrationBox.is( ':visible' ) ) {
            this.hideRegistrationBox();
            return;
        }

        var password = this.$el.find( '.login-password' ).val();

        this.setButtonsDisabled( true );

        options = {
            'error': _.bind( function( model, response ) {
                this.renderRegistrationErrors( response.responseJSON );
                this.setButtonsDisabled( false );
            }, this ),
        };
        this.model.login( email, password, options );
    },
    register: function() {
        /*
         * If the password row isn't visible, it means we're in the process
         * of resetting a password and have decided to cancel. So we need to
         * show the original login screen again.
         * There's probably a better way to do this, but for the time being,
         * this is the way.
         */
        if ( ! this.passwordRow.is( ':visible' ) ) {
            this.hidePasswordReset();
            return;
        }
        if ( ! this.registrationBox.is( ':visible' ) ) {
            this.showRegistrationBox();
            return;
        }
        var email = this.emailInput.val();
        var password = this.passwordInput.val();
        var confirmPassword = this.confirmPasswordInput.val();
        var firstName = this.firstNameInput.val();
        var lastName = this.lastNameInput.val();
        this.setButtonsDisabled( true );

        var options = {
            'error': _.bind( function( response ) {
                this.renderRegistrationErrors( response.responseJSON );
                this.setButtonsDisabled( false );
            }, this ),
            'success': _.bind( function() {
                this.renderRegistrationSuccess();
            }, this ),
        };

        this.model.register( email, 
                             password, 
                             confirmPassword, 
                             firstName, 
                             lastName,
                             options );
    },
    showPasswordReset: function() {
        this.passwordRow.addClass( 'hide' );
        this.registerButton.text( 'Cancel' );
        this.loginButton.text( 'Submit' );
    },
    hidePasswordReset: function() {
        this.passwordRow.removeClass( 'hide' );
        this.registerButton.text( 'Registration Form' );
        this.loginButton.text( 'Login' );
    },
    submitPasswordReset: function( email ) {
        this.setButtonsDisabled( true );
        var options = {
            'success': _.bind( function() {
                this.renderRegistrationSuccess();
            }, this ),
            'error': _.bind( function( errors ) {
                this.renderRegistrationErrors( errors );
                this.setButtonsDisabled( false );
            }, this ),
        };
        this.model.resetPassword( email, options );
    },
    inputChanged: function( e ) {
        $( e.target ).parents( '.error' ).removeClass( 'error' );

        if ( e.keyCode == 13 ) {
            if ( this.registrationBox.is( ':visible' ) ) {
                this.register();
            } else {
                this.login();
            }
        }
    },
    hideRegistrationBox: function() {
        this.hideRegistrationErrors();
        this.registrationBox.addClass( 'hidden' );
        this.forgotPassword.removeClass( 'hidden' );

        this.registerButton
            .removeClass( 'primary' )
            .addClass( 'secondary' )
            .text( 'Registration Form' );
        this.loginButton
            .removeClass( 'secondary' )
            .addClass( 'primary' )
            .text( 'Login' );
    }, 
    showRegistrationBox: function() {
        this.hideRegistrationErrors();
        this.registrationBox.removeClass( 'hidden' );
        this.forgotPassword.addClass( 'hidden' );

        this.registerButton
            .removeClass( 'secondary' )
            .addClass( 'primary' )
            .text( 'Register' );

        this.loginButton
            .removeClass( 'primary' )
            .addClass( 'secondary' )
            .text( 'Login Form' );

    },
    hideRegistrationErrors: function () {
        this.$el.find( '.error ').removeClass( 'error' );
    },
    setButtonsDisabled: function( disabled ) {
        this.registerButton.attr( 'disabled', disabled );
        this.loginButton.attr( 'disabled', disabled );
    },
    renderRegistrationSuccess: function() {
        this.hideRegistrationErrors();
        this.$el.find( '.registration-success-row' ).removeClass( 'hide' ); 
    },
    renderRegistrationErrors: function( errors ) {
        for ( var errorType in errors ) { // FIXME: Is this valid?
            var className = '.' + errorType + '-row';
            var row = this.$el.find( className );
            var errorList = row.find( '.error-message > ul' );
            var errorStrings = errors[ errorType ];

            errorList.empty();
            for( var i = 0; i < errorStrings.length; i++ ) {
                var error = errorStrings[ i ];
                errorList.append( $( '<li>' + error + '</li>' ) );
            }

            row.addClass( 'error' );
        }
    },
    render: function() {
        this.$el.html( this.template() );
        this.emailInput = this.$el.find( '.login-email-address' );
        this.passwordInput = this.$el.find( '.login-password' );
        this.confirmPasswordInput = this.$el.find( '.confirm-password' );
        this.firstNameInput = this.$el.find( '.first-name' );
        this.lastNameInput = this.$el.find( '.last-name' );
        this.registrationBox = this.$el.find( '.registration-box' );
        this.forgotPassword = this.$el.find( '.forgot-password' );
        this.passwordRow = this.$el.find( '.password-row' );

        this.registerButton = this.$el.find( '.register-button' );
        this.loginButton = this.$el.find( '.login-button' );
        return this;
    }
});

module.exports = LoginView;
