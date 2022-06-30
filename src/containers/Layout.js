import React from "react";
import { withRouter } from "react-router-dom";
import { PropTypes } from 'prop-types';
import DesktopContainer from './Layout/DesktopContainer'
import MobileContainer from './Layout/MobileContainer'

const ResponsiveContainer = ({ children }) => (
  <div>
    <DesktopContainer>{children}</DesktopContainer>
    <MobileContainer>{children}</MobileContainer>
  </div>
)

ResponsiveContainer.propTypes = {
  children: PropTypes.node,
}
class CustomLayout extends React.Component {
  render() {
    return (
      <ResponsiveContainer>
        <div>
          <h1>{this.props.children}</h1>
        </div>
      </ResponsiveContainer>
    );
  }
}

export default withRouter(
  (CustomLayout)
);
