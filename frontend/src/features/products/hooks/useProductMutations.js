import { useMutation, useQueryClient } from '@tanstack/react-query';
import { productsApi } from '../../../api/products';

export function useProductMutations(workspaceId) {
  const queryClient = useQueryClient();

  const createProduct = useMutation({
    mutationFn: (data) => productsApi.create(workspaceId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products', workspaceId] });
    },
  });

  const updateProduct = useMutation({
    mutationFn: ({ productId, data }) => productsApi.update(workspaceId, productId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products', workspaceId] });
    },
  });

  const deleteProduct = useMutation({
    mutationFn: (productId) => productsApi.delete(workspaceId, productId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products', workspaceId] });
    },
  });

  const tagPages = useMutation({
    mutationFn: ({ productId, pageIds }) => productsApi.tagPages(workspaceId, productId, pageIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products', workspaceId] });
    },
  });

  return {
    createProduct,
    updateProduct,
    deleteProduct,
    tagPages,
  };
}
