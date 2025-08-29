import { useState, useEffect } from 'react';

export const useApi = (apiFunction, dependencies = []) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiFunction();
      setData(response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const refetch = () => {
    fetchData();
  };

  useEffect(() => {
    fetchData();
  }, dependencies);

  return { data, loading, error, refetch };
};

export const usePagination = (initialPage = 1, limit = 10) => {
  const [page, setPage] = useState(initialPage);
  const [totalPages, setTotalPages] = useState(0);

  const nextPage = () => {
    if (page < totalPages) {
      setPage(page + 1);
    }
  };

  const prevPage = () => {
    if (page > 1) {
      setPage(page - 1);
    }
  };

  const goToPage = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setPage(pageNumber);
    }
  };

  return {
    page,
    totalPages,
    limit,
    setTotalPages,
    nextPage,
    prevPage,
    goToPage,
    hasNext: page < totalPages,
    hasPrev: page > 1
  };
};