import { Component } from "react";
import PropTypes from "prop-types";

class ErrorBoundary extends Component {
  state = { hasError: false, message: "" };

  static getDerivedStateFromError(error) {
    return { hasError: true, message: error.message };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-md mx-auto mt-20 text-center p-6 border rounded-xl">
          <h2 className="text-xl font-bold text-red-600">
            Something went wrong
          </h2>

          <p className="text-gray-500 mt-2 text-sm">
            {this.state.message}
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node,
};

export default ErrorBoundary;