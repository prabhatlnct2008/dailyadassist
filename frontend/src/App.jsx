import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ConversationProvider } from './context/ConversationContext';
import { WorkspaceProvider } from './context/WorkspaceContext';
import { PageProvider } from './context/PageContext';
import { ToastProvider } from './features/shared/Toast';
import { FullPageLoader } from './features/shared/Loader';

// Pages
import { LandingPage } from './features/landing/LandingPage';
import { LoginPage } from './features/auth/LoginPage';
import { AuthCallback } from './features/auth/AuthCallback';
import { SetupWizard } from './features/onboarding/SetupWizard';
import { WarRoom } from './features/warroom/WarRoom';
import { SettingsPage } from './features/settings/SettingsPage';

// Placeholder components for nested routes
// TODO: Implement these components in future phases
const AccountOverviewChat = () => <div className="p-6">Account Overview Chat - Coming Soon</div>;
const PageWarRoomChat = () => <div className="p-6">Page War Room Chat - Coming Soon</div>;
const LegacyArchiveViewer = () => <div className="p-6">Legacy Archive - Coming Soon</div>;

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <FullPageLoader />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return children;
}

function AppRoutes() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <FullPageLoader />;
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route
        path="/"
        element={
          isAuthenticated ? <Navigate to="/app" replace /> : <LandingPage />
        }
      />
      <Route
        path="/login"
        element={
          isAuthenticated ? <Navigate to="/app" replace /> : <LoginPage />
        }
      />
      <Route path="/auth/callback" element={<AuthCallback />} />

      {/* Protected routes */}
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute>
            <SetupWizard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <SettingsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <WorkspaceProvider>
              <PageProvider>
                <ConversationProvider>
                  <WarRoom />
                </ConversationProvider>
              </PageProvider>
            </WorkspaceProvider>
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="overview" replace />} />
        <Route path="overview" element={<AccountOverviewChat />} />
        <Route path="page/:pageId" element={<PageWarRoomChat />} />
        <Route path="archive" element={<LegacyArchiveViewer />} />
      </Route>

      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <ToastProvider>
            <AppRoutes />
          </ToastProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
