import { create } from 'zustand';

interface ThemeState {
  darkMode: boolean;
  toggleTheme: () => void;
  initTheme: () => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  darkMode: false,
  
  toggleTheme: () => set((state) => {
    const nextDark = !state.darkMode;
    if (nextDark) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
    localStorage.setItem('ssh_manager_dark_mode', String(nextDark));
    return { darkMode: nextDark };
  }),

  initTheme: () => {
    const saved = localStorage.getItem('ssh_manager_dark_mode');
    const isDark = saved === 'true' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
    
    if (isDark) {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
    
    set({ darkMode: isDark });
  }
}));
