import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GalaxyDemo } from './3d/components/GalaxyDemo';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div style={{ width: '100vw', height: '100vh', margin: 0, padding: 0 }}>
        {/* 3D Galaxy Scene with Procedural Star Field */}
        <GalaxyDemo />
      </div>
    </QueryClientProvider>
  );
}

export default App;
