var mongoose = require('mongoose');
var bcrypt = require('bcrypt');

// define a schema for db in here, and export that schema
// props in the schema: email is the key
// these schemas are for each inst 'user' in the table 'User'
var UserSchema = new mongoose.Schema({
    email: {
        type: String,
        index: {unique: true}
    },
    password: String
});

// define a method
// note: all props and methods are for insts
// cP takes in a psw, compare this inst's psw with it,
// store compRes in vars, and the clb acts on these res
UserSchema.methods.comparePassword = function comparePassword(password, callback) {
    bcrypt.compare(password, this.password, callback);
}

// before saving the email-psw pair, we shall do some proc on the psw to be saved:
// salting and hashing
UserSchema.pre('save', function saveHook(next) {
    var user = this;
    
    if(!user.isModified('password')) return next();
    return bcrypt.genSalt((saltError, salt) => {
        if (saltError) {
            return next(saltError);
        }
        return bcrypt.hash(user.password, salt, (hashError, hash) => {
            if (hashError) {
                return next(hashError);
            }
            user.password = hash;
            return next();
        });
    });
});

// under this schema, we set up a 'table' called User
module.exports = mongoose.model('User', UserSchema);