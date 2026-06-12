import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-dark-bg transition-colors duration-200">
      {/* Sidebar */}
      <Sidebar collapsed={collapsed} />

      {/* Main Content Area */}
      <div
        className="flex-1 flex flex-col min-h-screen transition-all duration-300"
        style={{ paddingLeft: collapsed ? '80px' : '264px' }}
      >
        {/* Header */}
        <Header
          sidebarCollapsed={collapsed}
          setSidebarCollapsed={setCollapsed}
        />

        {/* Dynamic page container */}
        <main className="flex-1 p-6 mt-16 max-w-[1600px] w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
