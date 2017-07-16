var User = require('mongoose').model('User');
var PassportLocalStrategy = require('passport-local').Strategy;

// here when saving, if email already in db, 
// the mongo shall throw an error
module.exports = new PassportLocalStrategy({
    usernameField: 'email',
    passwordField: 'password',
    passReqToCallback: true
}, (req, email, password, done) => {
    var userData = {
        email: email.trim(),
        password: password.trim(),
    };

    // creating a new inst of User and try to .save it in User table
    var user = new User(userData);
    user.save((err) => {
        console.log('Saving new user!');
        if (err) {
            return done(err);
        }
        return done(null);
    });
});