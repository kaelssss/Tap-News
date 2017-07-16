var express = require('express');
var passport = require('passport');
var router = express.Router();
var validator = require('validator');

router.post('/signup', (req, res, next) => {
    var validationResult = validateSignupForm(req.body);
    if (!validationResult.success) {
        console.log('validationResult failed');
        
        return res.status(400).json({
            success: false,
            message: validationResult.message,
            errors: validationResult.errors
        });
    }

    return passport.authenticate('local-signup', (err) => {
        if (err) {
            console.log(err);
            if (err.name === 'MongoError' && err.code === 11000) {
                // the 11000 Mongo code is for a duplication email error
                // the 409 HTTP status code is for conflict error
                return res.status(409).json({
                    success: false,
                    message: 'Check the form for errors.',
                    errors: {
                        email: 'This email is already taken.'
                    }
                });
            }

            return res.status(400).json({
                success: false,
                message: 'Could not process the form.'
            });
        }

        return res.status(200).json({
            success: true,
            message: 'You have successfully signed up! Now you should be able to log in.'
        });
        
    })(req, res, next);
});

router.post('/login', (req, res, next) => {
    var validationResult = validateLoginForm(req.body);
    if (!validationResult.success) {
        return res.status(400).json({
            success: false,
            message: validationResult.message,
            errors: validationResult.errors
        });
    }

    return passport.authenticate('local-login', (err, token, userData) => {
        if (err) {
            if (err.name === 'IncorrectCredentialsError') {
                return res.status(400).json({
                    success: false,
                    message: err.message
                });
            }

            return res.status(400).json({
                success: false,
                message: 'Could not process the form: ' + err.message
            });
        }

        return res.json({
            success: true,
            message: 'You have successfully logged in!',
            token,
            user: userData
        });
        
    })(req, res, next);
});

var validateSignupForm = function(body) {
    console.log(body);
    const errors = {};
    let isFormValid = true;
    let message = '';

    if (!body || typeof body.email !== 'string' || !validator.isEmail(body.email)) {
        isFormValid = false;
        errors.email = 'Please provide a correct email address.';
    }

    if (!body || typeof body.password !== 'string' || body.password.trim().length < 8) {
        isFormValid = false;
        errors.password = 'Password must have at least 8 characters.';
    }

    if (!isFormValid) {
        message = 'Check the form for errors.';
    }

    return {
        success: isFormValid,
        message,
        errors
    };
}

var validateLoginForm = function(body) {
    console.log(body);
    const errors = {};
    let isFormValid = true;
    let message = '';

    if (!body || typeof body.email !== 'string' || body.email.trim().length === 0) {
        isFormValid = false;
        errors.email = 'Please provide your email address.';
    }

    if (!body || typeof body.password !== 'string' || body.password.trim().length === 0) {
        isFormValid = false;
        errors.password = 'Please provide your password.';
    }

    if (!isFormValid) {
        message = 'Check the form for errors.';
    }

    return {
        success: isFormValid,
        message,
        errors
    };
}

module.exports = router;