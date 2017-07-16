import React from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import './SignupForm.css';

class SignupForm extends React.Component {
    render() {
        return (
            <div className="container">
                <div className="card-panel signup-panel">
                <form className="col s12" action="/" onSubmit={this.props.onSubmit}>
                    <h4 className="center-align">Sign Up</h4>
                    {this.props.errors.summary && <div className="row"><p className="error-message">{this.props.errors.summary}</p></div>}
                    <div className="row">
                    <div className="input-field col s12">
                        <input id="email" type="email" name="email" className="validate" onChange={this.props.onChange}/>
                        <label htmlFor="email">Email</label>
                    </div>
                    </div>
                    {this.props.errors.email && <div className="row"><p className="error-message">{this.props.errors.email}</p></div>}
                    <div className="row">
                    <div className="input-field col s12">
                        <input id="password" type="password" name="password" className="validate" onChange={this.props.onChange}/>
                        <label htmlFor="password">Password</label>
                    </div>
                    </div>
                    {this.props.errors.password && <div className="row"><p className="error-message">{this.props.errors.password}</p></div>}
                    <div className="row">
                    <div className="input-field col s12">
                        <input id="confirm_password" type="password" name="confirm_password" className="validate" onChange={this.props.onChange}/>
                        <label htmlFor="confirm_password">Confirm Password</label>
                    </div>
                    </div>
                    <div className="row right-align">
                    <input type="submit" className="waves-effect waves-light btn indigo lighten-1" value='Sign Up'/>
                    </div>
                    <div className="row">
                    <p className="right-align"> Already have an account? <Link to="/login">Login</Link></p>
                    </div>
                </form>
                </div>
            </div>
        );
    }
}

SignupForm.PropTypes = {
    onSubmit: PropTypes.func.isRequired,
    onChange: PropTypes.func.isRequired,
    errors: PropTypes.object.isRequired
};

export default SignupForm;