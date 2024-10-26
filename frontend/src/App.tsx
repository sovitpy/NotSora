import { ThemeProvider } from "@/components/theme-provider"
import VideoPromptPlayer from "./components/ui/VideoPromptPlayer";
import { ModeToggle } from "./components/mode-toggle";

export function App() {
  return (
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <ModeToggle />
      <VideoPromptPlayer />
  </ThemeProvider>
  )
}

export default App;
