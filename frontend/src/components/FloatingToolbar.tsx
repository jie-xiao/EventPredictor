import { useState, useEffect, useCallback } from 'react';
import {
  Menu,
  BarChart3,
  List,
  Users,
  Moon,
  Sun,
  Settings,
  RefreshCw,
} from 'lucide-react';
import '../styles/drawer-toolbar.css';

export interface FloatingToolbarProps {
  onToggleRightDrawer?: () => void;
  onToggleLeftDrawer?: () => void;
  onToggleBottomDrawer?: () => void;
  onRefresh?: () => void;
  onSettings?: () => void;
  rightDrawerOpen?: boolean;
  leftDrawerOpen?: boolean;
  bottomDrawerOpen?: boolean;
  isRefreshing?: boolean;
}

interface ToolbarButton {
  id: string;
  icon: React.ReactNode;
  tooltip: string;
  shortcut?: string;
  onClick?: () => void;
  active?: boolean;
  loading?: boolean;
  toggle?: boolean;
}

export default function FloatingToolbar({
  onToggleRightDrawer,
  onToggleLeftDrawer,
  onToggleBottomDrawer,
  onRefresh,
  onSettings,
  rightDrawerOpen = false,
  leftDrawerOpen = false,
  bottomDrawerOpen = false,
  isRefreshing = false,
}: FloatingToolbarProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);

  // 键盘快捷键
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Esc 键收起工具栏或关闭抽屉
      if (e.key === 'Escape') {
        if (isExpanded) {
          setIsExpanded(false);
        }
        return;
      }

      // 其他快捷键需要工具栏展开时才生效
      if (!isExpanded) return;

      switch (e.key.toLowerCase()) {
        case 'a':
          onToggleRightDrawer?.();
          break;
        case 'e':
          onToggleBottomDrawer?.();
          break;
        case 'r':
          onToggleLeftDrawer?.();
          break;
        case 't':
          setIsDarkMode(!isDarkMode);
          break;
        case 's':
          onSettings?.();
          break;
        case 'f5':
          e.preventDefault();
          onRefresh?.();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isExpanded, isDarkMode, onToggleRightDrawer, onToggleBottomDrawer, onToggleLeftDrawer, onSettings, onRefresh]);

  const handleThemeToggle = useCallback(() => {
    setIsDarkMode(!isDarkMode);
    // 这里可以添加主题切换的实际逻辑
  }, [isDarkMode]);

  const buttons: ToolbarButton[] = [
    {
      id: 'analysis',
      icon: <BarChart3 />,
      tooltip: 'Analysis Panel',
      shortcut: 'A',
      onClick: onToggleRightDrawer,
      active: rightDrawerOpen,
      toggle: true,
    },
    {
      id: 'events',
      icon: <List />,
      tooltip: 'Event List',
      shortcut: 'E',
      onClick: onToggleBottomDrawer,
      active: bottomDrawerOpen,
      toggle: true,
    },
    {
      id: 'roles',
      icon: <Users />,
      tooltip: 'Role Details',
      shortcut: 'R',
      onClick: onToggleLeftDrawer,
      active: leftDrawerOpen,
      toggle: true,
    },
    {
      id: 'theme',
      icon: isDarkMode ? <Moon /> : <Sun />,
      tooltip: isDarkMode ? 'Dark Mode' : 'Light Mode',
      shortcut: 'T',
      onClick: handleThemeToggle,
      active: !isDarkMode,
    },
    {
      id: 'settings',
      icon: <Settings />,
      tooltip: 'Settings',
      shortcut: 'S',
      onClick: onSettings,
    },
    {
      id: 'refresh',
      icon: <RefreshCw />,
      tooltip: 'Refresh Data',
      shortcut: 'F5',
      onClick: onRefresh,
      loading: isRefreshing,
    },
  ];

  return (
    <div className={`floating-toolbar ${isExpanded ? 'expanded' : ''}`}>
      {/* 主菜单按钮 */}
      <button
        className="toolbar-btn primary"
        onClick={() => setIsExpanded(!isExpanded)}
        data-tooltip={isExpanded ? 'Collapse (Esc)' : 'Expand Menu'}
        aria-label="Toggle toolbar menu"
      >
        <Menu />
        <span className="shortcut">Esc</span>
      </button>

      {/* 功能按钮 */}
      {buttons.map((btn) => (
        <button
          key={btn.id}
          className={`toolbar-btn ${btn.active ? 'active' : ''} ${btn.loading ? 'loading' : ''}`}
          onClick={btn.onClick}
          data-tooltip={btn.tooltip}
          aria-label={btn.tooltip}
        >
          {btn.icon}
          {btn.shortcut && <span className="shortcut">{btn.shortcut}</span>}
        </button>
      ))}
    </div>
  );
}
