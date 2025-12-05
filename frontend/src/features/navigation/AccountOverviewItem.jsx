import { NavLink } from 'react-router-dom';

export function AccountOverviewItem() {
  return (
    <NavLink
      to="/app/overview"
      className={({ isActive }) =>
        `flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
          isActive
            ? 'bg-primary-50 text-primary-700 font-medium'
            : 'text-gray-700 hover:bg-gray-100'
        }`
      }
    >
      <svg
        className="w-5 h-5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      </svg>
      <span>Account Overview</span>
    </NavLink>
  );
}

export default AccountOverviewItem;
