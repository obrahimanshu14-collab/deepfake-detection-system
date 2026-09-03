import PropTypes from "prop-types";
import { Navigate, useLocation } from "react-router-dom";
import { isLoggedIn } from "../services/authService";

function ProtectedRoute({ children }) {
  const location = useLocation();
  if (!isLoggedIn()) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return children;
}

ProtectedRoute.propTypes = { children: PropTypes.node.isRequired };

export default ProtectedRoute;
