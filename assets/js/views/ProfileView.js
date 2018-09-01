var Backbone = require('backbone');
var _ = require('underscore');
var $ = require('jquery');

var ProfileView = Backbone.View.extend({
    className: 'profile-view', 
    template: _.template( require('./../templates/profile-template') ),
    events: {
        'click .save-image': 'saveImage',
        'click .save-password': 'savePassword',
        'click .submit-blurb': 'saveBlurb',
        'keydown .original-password': 'checkSubmit',
        'keydown .new-password': 'checkSubmit',
        'keydown .confirm-password': 'checkSubmit',
        'change .new-photo-field': 'photoChanged',
    },
    photoChanged: function() {
        var hasPhoto = Boolean( this.$el.find( '.new-photo-field' ).val() );
        this.$el.find( '.save-image' ).prop( 'disabled', ! hasPhoto );
    },
    checkSubmit: function ( e ) {
        if ( e.keyCode == 13 ) {
            this.savePassword();
        }
    },
    imageUploadFailed: function( user, reason ) {
    },
    saveImage: function() {
        var newPhoto = this.$el.find( '.new-photo-field' ).get( 0 ).files[0];
        this.model.setPhoto( newPhoto, { 'error': _.bind( this.imageUploadFailed, this ) } );
    },
    savePassword: function() {
        var original = this.$el.find( '.original-password' ).val();
        var newPassword = this.$el.find( '.new-password' ).val();
        var confirmPassword = this.$el.find( '.confirm-password' ).val();
        
        if ( ! Boolean( original ) || ! Boolean( newPassword ) || ! Boolean( confirmPassword ) ) {
        }
    },
    saveBlurb: function() {
        var newBlurb = this.$el.find( '.user-blurb' ).val();
        this.model.save( { 'blurb': newBlurb }, { 'patch': true, 'silent': true } );
    },
    render: function() {
        /* Create the listener on the first render */
        this.listenTo( this.model, 'change', this.render );
        this.$el.html( this.template( this.model.attributes ) );
        this.delegateEvents();
        return this;
    }
});

module.exports = ProfileView;
