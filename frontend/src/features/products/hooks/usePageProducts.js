import { useQuery } from '@tanstack/react-query';
import { productsApi } from '../../../api/products';

export function usePageProducts(workspaceId, pageId, options = {}) {
  return useQuery({
    queryKey: ['products', workspaceId, 'page', pageId],
    queryFn: () => productsApi.listForPage(workspaceId, pageId),
    enabled: !!workspaceId && !!pageId,
    ...options,
  });
}
