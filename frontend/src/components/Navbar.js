import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-gray-800 p-4" role="navigation">
      <div className="container mx-auto flex justify-between items-center">
        <Link to="/" className="text-white text-xl font-bold">
          Fitness Planner
        </Link>
        <div className="space-x-4">
          <Link to="/" className="text-gray-300 hover:text-white">
            Home
          </Link>
          <Link to="/form" className="text-gray-300 hover:text-white">
            Create Plan
          </Link>
          <Link to="/results" className="text-gray-300 hover:text-white">
            Results
          </Link>
          <Link to="/login" className="text-gray-300 hover:text-white">
            Login
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
