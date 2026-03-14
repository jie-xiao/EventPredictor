import { useState } from 'react';
import { X, Search } from 'lucide-react';
import '../styles/drawer-toolbar.css';

export interface Role {
  id: string;
  name: string;
  flag?: string;
  type: 'government' | 'enterprise' | 'public' | 'media' | 'other';
  stance: string;
  confidence: number;
  description?: string;
}

export interface LeftDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  roles?: Role[];
  selectedRoleId?: string;
  onRoleSelect?: (role: Role) => void;
}

const roleTypeLabels: Record<Role['type'], string> = {
  government: 'Government',
  enterprise: 'Enterprise',
  public: 'Public',
  media: 'Media',
  other: 'Other',
};

const roleTypeFilters = ['All', 'Government', 'Enterprise', 'Public', 'Media'];

export default function LeftDrawer({
  isOpen,
  onClose,
  roles = [],
  selectedRoleId,
  onRoleSelect,
}: LeftDrawerProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');

  const filteredRoles = roles.filter((role) => {
    const matchesSearch =
      role.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      role.stance.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesFilter =
      activeFilter === 'All' || roleTypeLabels[role.type] === activeFilter;

    return matchesSearch && matchesFilter;
  });

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'from-green-500 to-emerald-500';
    if (confidence >= 60) return 'from-yellow-500 to-amber-500';
    return 'from-red-500 to-orange-500';
  };

  return (
    <>
      {/* 遮罩层 */}
      <div
        className={`drawer-overlay ${isOpen ? 'visible' : ''}`}
        onClick={onClose}
      />

      {/* 抽屉面板 */}
      <div className={`drawer-left ${isOpen ? 'open' : ''}`}>
        {/* Header */}
        <div className="drawer-header">
          <span className="text-lg font-semibold text-text-primary">Roles</span>
          <div className="flex items-center gap-2">
            <span className="text-sm text-text-muted">{roles.length} total</span>
            <button
              className="drawer-close-btn"
              onClick={onClose}
              aria-label="Close drawer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Search */}
        <div className="drawer-search">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
            <input
              type="text"
              placeholder="Search roles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input pl-9"
            />
          </div>
        </div>

        {/* Tabs */}
        <div className="drawer-tabs">
          {roleTypeFilters.map((filter) => (
            <button
              key={filter}
              className={`tab-btn ${activeFilter === filter ? 'active' : ''}`}
              onClick={() => setActiveFilter(filter)}
            >
              {filter}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="drawer-content">
          {filteredRoles.length === 0 ? (
            <div className="text-center py-8 text-text-muted">
              <p>No roles found</p>
              {searchQuery && (
                <button
                  className="mt-2 text-sm text-primary-cyan hover:underline"
                  onClick={() => setSearchQuery('')}
                >
                  Clear search
                </button>
              )}
            </div>
          ) : (
            filteredRoles.map((role) => (
              <div
                key={role.id}
                className={`role-card ${selectedRoleId === role.id ? 'selected border-primary-cyan' : ''}`}
                onClick={() => onRoleSelect?.(role)}
              >
                <div className="role-header">
                  {role.flag && (
                    <span className="text-xl">{role.flag}</span>
                  )}
                  <span className="role-name">{role.name}</span>
                </div>
                <p className="role-stance">{role.stance}</p>
                <div className="role-confidence">
                  <div className="confidence-bar">
                    <div
                      className={`confidence-fill bg-gradient-to-r ${getConfidenceColor(role.confidence)}`}
                      style={{ width: `${role.confidence}%` }}
                    />
                  </div>
                  <span className="confidence-value">{role.confidence}%</span>
                </div>
                {role.description && (
                  <p className="mt-2 text-xs text-text-muted line-clamp-2">
                    {role.description}
                  </p>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
}
