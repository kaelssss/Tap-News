var jwt = require('jsonwebtoken');
var User = require('mongoose').model('User');
var PassportLocalStrategy = require('passport-local').Strategy;
var config = require('../config/config.json');

// a strategy of a psp-lcl has:
// (1)  first obj as an option field names selections:
//      by default, psp stg looks in the field passed to it for field names 'username' and 'passport'
//      if ur form have other field names instead of them, u should tell it in option
// (2)  second func editing dones:
//      u can take ur field names as vars got from the form, like email;
//      note that I also passed the req(which is the form) to the func,
//      so the following func has 4 paras
var stg = new PassportLocalStrategy({
    usernameField: 'email',
    passwordField: 'password',
    //passReqToCallback: true
}, (email, password, done) => {
    var userData = {
        email: email.trim(),
        password: password.trim()
    };

    return User.findOne({ email: userData.email }, (err, user) => {
        if (err) {
            return done(err);
        }
        if (!user) {
            const error = new Error('Incorrect email or password');
            error.name = 'IncorrectCredentialsError';
            return done(error);
        }
        
        // a call to the inst's method, like we mentioned in model/user,
        // that callback be called taking in err and succBool got by
        // bcrypt.compare()
        //-> it is designed in bcrypt that the third triggered clb takes in err and res(succBool)
        return user.comparePassword(userData.password, (passwordErr, isMatch) => {
            if (err) {
                return done(err);
            }
            if (!isMatch) {
                var error = new Error('Incorrect email or password');
                error.name = 'IncorrectCredentialsError';
                return done(error);
            }
            
            // here: succ, preparing a tkn for u
            var payload = {
                sub: user._id
            };
            var token = jwt.sign(payload, config.jwtSecret);
            var data = {
                name: user.email
            };
            return done(null, token, data);
        });
    });
});

module.exports = stg;