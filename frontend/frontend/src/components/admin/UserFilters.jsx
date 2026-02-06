import React from 'react';
import styles from './UserFilters.module.css';

const UserFilters = ({ filters, onFilterChange }) => {
  const handleSearchChange = (e) => {
    onFilterChange({
      ...filters,
      search: e.target.value
    });
  };

  const handlePlanChange = (e) => {
    const value = e.target.value;
    onFilterChange({
      ...filters,
      plan: value === 'all' ? null : value
    });
  };

  const handleBlockedChange = (e) => {
    const value = e.target.value;
    onFilterChange({
      ...filters,
      is_blocked: value === 'all' ? null : value === 'blocked'
    });
  };

  const handleClearFilters = () => {
    onFilterChange({
      plan: null,
      is_blocked: null,
      search: ''
    });
  };

  const hasActiveFilters = filters.plan || filters.is_blocked !== null || filters.search;

  return (
    <div className={styles.container}>
      <div className={styles.filters}>
        {/* Search */}
        <div className={styles.filterGroup}>
          <label className={styles.label}>🔍 Buscar por email</label>
          <input
            type="text"
            value={filters.search}
            onChange={handleSearchChange}
            placeholder="email@example.com"
            className={styles.input}
          />
        </div>

        {/* Plan Filter */}
        <div className={styles.filterGroup}>
          <label className={styles.label}>💎 Plan</label>
          <select
            value={filters.plan || 'all'}
            onChange={handlePlanChange}
            className={styles.select}
          >
            <option value="all">Todos los planes</option>
            <option value="FREE">FREE</option>
            <option value="BASIC">BASIC</option>
            <option value="PRO">PRO</option>
          </select>
        </div>

        {/* Blocked Filter */}
        <div className={styles.filterGroup}>
          <label className={styles.label}>🚫 Estado</label>
          <select
            value={
              filters.is_blocked === null 
                ? 'all' 
                : filters.is_blocked 
                  ? 'blocked' 
                  : 'active'
            }
            onChange={handleBlockedChange}
            className={styles.select}
          >
            <option value="all">Todos</option>
            <option value="active">Activos</option>
            <option value="blocked">Bloqueados</option>
          </select>
        </div>

        {/* Clear Filters */}
        {hasActiveFilters && (
          <div className={styles.filterGroup}>
            <label className={styles.label}>&nbsp;</label>
            <button onClick={handleClearFilters} className={styles.clearButton}>
              ✕ Limpiar filtros
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserFilters;