import { useQuery } from '@tanstack/react-query';
import { productsApi } from '../../../api/products';

export function useProducts(workspaceId, options = {}) {
  return useQuery({
    queryKey: ['products', workspaceId],
    queryFn: () => productsApi.list(workspaceId),
    enabled: !!workspaceId,
    ...options,
  });
}

export function useProduct(workspaceId, productId, options = {}) {
  return useQuery({
    queryKey: ['products', workspaceId, productId],
    queryFn: () => productsApi.get(workspaceId, productId),
    enabled: !!workspaceId && !!productId,
    ...options,
  });
}
