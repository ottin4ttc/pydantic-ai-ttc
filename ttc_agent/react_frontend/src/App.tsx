import ChatContainer from './components/chat/ChatContainer';
import { Toaster } from './components/ui/toaster';

function App() {
  return (
    <div className="container py-8">
      <ChatContainer />
      <Toaster />
    </div>
  );
}

export default App;
