import React from 'react';
import PropTypes from 'prop-types';
import SignupForm from './SignupForm';

class SignupPage extends React.Component {
    constructor(props, context) {
        super(props, context);
        this.state = {
            errors: {
                summary: '',
                email: '',
                password: ''
            },
            userInfo: {
                email: '',
                password: '',
                confirm_password: ''
            }
        };
        this.processForm = this.processForm.bind(this);
        this.changeInfo = this.changeInfo.bind(this);
    }

    processForm(event) {
        event.preventDefault();
        const email = this.state.userInfo.email;
        const password = this.state.userInfo.password;
        const confirm_password = this.state.userInfo.confirm_password;
        console.log(email + ' : ' + password + ' : ' + confirm_password);
        if(password !== confirm_password) {
            return;
        }
        // fetch: make request, and clb the response
        fetch('http://localhost:3000/auth/signup', {
            method: 'POST',
            cache: false,
            headers: {
                'Accept': 'application/json',
                'Content-type': 'application/json'
            },
            body: JSON.stringify({
                email: this.state.userInfo.email,
                password: this.state.userInfo.password
            })
        }).then((res) => {
            if(res.status === 200) {
                this.setState({
                    errors: {}
                });
                this.context.router.replace('/login');
            }
            else {
                console.log('Signup failed');
                res.json().then((json) => {
                    const errors = json.errors? json.errors:{};
                    errors.summary = json.message;
                    this.setState({
                        errors: errors
                    });
                });
            }
        });
    }

    // note that here, we are only adding a part of code based on the previous onChange;
    // if we do not want that, like in procForm, prevent that default
    // the default handler is like: showing it...
    changeInfo(event) {
        const field = event.target.name;
        const userInfo = this.state.userInfo;
        userInfo[field] = event.target.value;
        this.setState({
            userInfo: userInfo
        });
        
        if(this.state.userInfo.password !== this.state.userInfo.confirm_password) {
            const errors = this.state.errors;
            errors.password = 'Not matched!';
            this.setState({
                errors: errors
            });
        }
        else {
            const errors = this.state.errors;
            errors.password = '';
            this.setState({
                errors: errors
            });
        }
    }

    render() {
        return (
            <SignupForm 
            onSubmit={this.processForm}
            onChange={this.changeInfo}
            errors={this.state.errors}
            />
        );
    }
}

SignupPage.contextTypes = {
  router: PropTypes.object.isRequired
};

export default SignupPage;