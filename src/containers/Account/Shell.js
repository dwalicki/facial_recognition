import React from 'react';
import {
    Grid,
    Container,
    Segment,
    Header,
    Menu
} from 'semantic-ui-react';
import { withRouter } from "react-router-dom";
import { logout } from '../../store/actions/auth';
import { connect } from "react-redux";

const Shell = props => (
    <Segment vertical>
        <Container>
            <Grid container stackable verticalAlign="top" divided columns={2}>
                <Grid.Row>
                    <Grid.Column width={8}>
                        <Header as="h3">Account</Header>
                        <Menu vertical fluid>
                            <Menu.Item
                                active={props.location.pathname === '/account/change-email'}
                                onClick={() => props.history.push("/account/change-email")}
                                name="change-email"
                            >
                                Change Email
                            </Menu.Item>
                            <Menu.Item
                                active={props.location.pathname === '/account/change-password'}
                                onClick={() => props.history.push("/account/change-password")}
                                name="change-password"
                            >
                                Change Password
                            </Menu.Item>
                            <Menu.Item
                                active={props.location.pathname === '/account/billing'}
                                onClick={() => props.history.push("/account/billing")}
                                name="billing"
                            >
                                Billing
                            </Menu.Item>
                            <Menu.Item
                                active={props.location.pathname === '/account/api-key'}
                                onClick={() => props.history.push("/account/api-key")}
                                name="api-key"
                            >
                                API Key
                            </Menu.Item>
                            <Menu.Item name="logout" onClick={() => props.logout()}>
                                Logout
                            </Menu.Item>
                        </Menu>
                    </Grid.Column>
                    <Grid.Column width={8}>
                        {props.children}
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </Container>
    </Segment>
);

const mapDispatchToProps = dispatch => {
    return {
        logout: () => dispatch(logout())
    };
};

export default withRouter(
    connect(
        null,
        mapDispatchToProps,
    )(Shell)
);
