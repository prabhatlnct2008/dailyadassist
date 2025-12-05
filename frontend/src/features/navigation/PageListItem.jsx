import { NavLink } from 'react-router-dom';

export function PageListItem({ page }) {
  const { id, facebook_page, default_tone, is_primary } = page;
  const { name, picture } = facebook_page;

  return (
    <NavLink
      to={`/app/page/${id}`}
      className={({ isActive }) =>
        `flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
          isActive
            ? 'bg-primary-50 text-primary-700 font-medium'
            : 'text-gray-700 hover:bg-gray-100'
        }`
      }
    >
      {/* Page Avatar */}
      <div className="flex-shrink-0">
        {picture ? (
          <img
            src={picture}
            alt={name}
            className="w-8 h-8 rounded-full"
          />
        ) : (
          <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center">
            <svg
              className="w-5 h-5 text-gray-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}
      </div>

      {/* Page Name and Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm truncate">{name}</p>
        {default_tone && (
          <p className="text-xs text-gray-500">{default_tone}</p>
        )}
      </div>

      {/* Primary Badge */}
      {is_primary && (
        <span className="flex-shrink-0 text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded">
          Primary
        </span>
      )}
    </NavLink>
  );
}

export default PageListItem;
