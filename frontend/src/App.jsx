import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ConversationProvider } from './context/ConversationContext';
import { ToastProvider } from './features/shared/Toast';
import { FullPageLoader } from './features/shared/Loader';

// Pages
import { LandingPage } from './features/landing/LandingPage';
import { LoginPage } from './features/auth/LoginPage';
import { AuthCallback } from './features/auth/AuthCallback';
import { SetupWizard } from './features/onboarding/SetupWizard';
import { WarRoom } from './features/warroom/WarRoom';
import { AccountOverview } from './features/warroom/AccountOverview';
import { PageChat } from './features/warroom/PageChat';
import { SettingsPage } from './features/settings/SettingsPage';

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
      {/* App routes with nested routing */}
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <ConversationProvider>
              <WarRoom />
            </ConversationProvider>
          </ProtectedRoute>
        }
      >
        {/* Default redirect to overview */}
        <Route index element={<Navigate to="/app/overview" replace />} />

        {/* Account overview route */}
        <Route path="overview" element={<AccountOverview />} />

        {/* Page-specific chat route */}
        <Route path="page/:pageId" element={<PageChat />} />

        {/* Archive route (placeholder for future) */}
        <Route
          path="archive"
          element={
            <div className="flex items-center justify-center h-full">
              <p className="text-gray-500">Archive feature coming soon</p>
            </div>
          }
        />
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
