import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToastStore } from '../../store/toastStore';
import { listUsers } from '../../services/admin';
import UserTable from '../../components/admin/UserTable';
import UserFilters from '../../components/admin/UserFilters';
import styles from './AdminUsers.module.css';

const AdminUsers = () => {
  const navigate = useNavigate();
  const showToast = useToastStore((state) => state.showToast);
  
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    total: 0,
    skip: 0,
    limit: 20
  });
  
  const [filters, setFilters] = useState({
    plan: null,
    is_blocked: null,
    search: ''
  });

  useEffect(() => {
    fetchUsers();
  }, [pagination.skip, pagination.limit, filters.plan, filters.is_blocked]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await listUsers({
        skip: pagination.skip,
        limit: pagination.limit,
        plan: filters.plan,
        is_blocked: filters.is_blocked
      });
      
      setUsers(data.users);
      setPagination(prev => ({
        ...prev,
        total: data.total
      }));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching users:', error);
      showToast('Error al cargar usuarios', 'error');
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPagination(prev => ({ ...prev, skip: 0 })); // Reset to first page
  };

  const handlePageChange = (newPage) => {
    setPagination(prev => ({
      ...prev,
      skip: newPage * prev.limit
    }));
  };

  const handleUserClick = (userId) => {
    navigate(`/admin/users/${userId}`);
  };

  const handleRefresh = () => {
    fetchUsers();
    showToast('Lista actualizada', 'success');
  };

  // Filtrar por búsqueda local (email)
  const filteredUsers = users.filter(user => {
    if (!filters.search) return true;
    return user.email.toLowerCase().includes(filters.search.toLowerCase());
  });

  const currentPage = Math.floor(pagination.skip / pagination.limit);
  const totalPages = Math.ceil(pagination.total / pagination.limit);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Gestión de Usuarios</h1>
          <p className={styles.subtitle}>
            {pagination.total} usuarios totales
          </p>
        </div>
        <button onClick={handleRefresh} className={styles.refreshButton}>
          🔄 Actualizar
        </button>
      </div>

      <UserFilters 
        filters={filters} 
        onFilterChange={handleFilterChange}
      />

      {loading ? (
        <div className={styles.loading}>Cargando usuarios...</div>
      ) : (
        <>
          <UserTable 
            users={filteredUsers}
            onUserClick={handleUserClick}
          />

          {/* Pagination */}
          {totalPages > 1 && (
            <div className={styles.pagination}>
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 0}
                className={styles.paginationButton}
              >
                ← Anterior
              </button>
              
              <span className={styles.paginationInfo}>
                Página {currentPage + 1} de {totalPages}
              </span>
              
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= totalPages - 1}
                className={styles.paginationButton}
              >
                Siguiente →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AdminUsers;