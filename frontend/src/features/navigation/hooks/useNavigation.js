import { useLocation, useNavigate, useParams } from 'react-router-dom';

export function useNavigation() {
  const location = useLocation();
  const navigate = useNavigate();
  const params = useParams();

  const isOnOverview = location.pathname === '/app/overview' || location.pathname === '/app';
  const isOnPage = location.pathname.startsWith('/app/page/');
  const currentPageId = params.pageId;

  const navigateToOverview = () => {
    navigate('/app/overview');
  };

  const navigateToPage = (pageId) => {
    navigate(`/app/page/${pageId}`);
  };

  const navigateToArchive = () => {
    navigate('/app/archive');
  };

  return {
    location,
    navigate,
    params,
    isOnOverview,
    isOnPage,
    currentPageId,
    navigateToOverview,
    navigateToPage,
    navigateToArchive,
  };
}

export default useNavigation;
