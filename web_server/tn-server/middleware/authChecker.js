var jwt = require('jsonwebtoken');
var User = require('mongoose').model('User');
var config = require('../config/config.json');

var authChecker = function(req, res, next) {
    console.log('auth_checker: req: ' + req.headers);

    // we will include the auz in req's headers if we have the tkn
    if (!req.headers.authorization) {
        return res.status(401).end();
    }

    // but the tkn we sent u is like "bearer token-value"
    // where bearer is the name of ptcl
    var token = req.headers.authorization.split(' ')[1];
    console.log('auth_checker: token: ' + token);
    // decode the token, get the user_id in payload's sub,
    // and go to the db to see if there is such a id (we used id of db as key)
    return jwt.verify(token, config.jwtSecret, (err, decoded) => {
        if (err) { return res.status(401).end(); }

        var id = decoded.sub;
        return User.findById(id, (userErr, user) => {
        if (userErr || !user) {
            return res.status(401).end();
        }
        return next();
        });
    });
};

module.exports = authChecker;