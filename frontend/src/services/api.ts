
// API service for fetching products from a real API

// Base API URL
const API_URL = 'https://fakestoreapi.com';

export interface ApiProduct {
  id: number;
  title: string;
  price: number;
  description: string;
  category: string;
  image: string;
  rating: {
    rate: number;
    count: number;
  };
}

export interface FormattedProduct {
  id: string;
  name: string;
  description: string;
  price: number;
  salePrice?: number;
  category: string;
  image: string;
  rating: number;
  reviewCount: number;
  features: string[];
  colors?: string[];
  sizes?: string[];
  isNew?: boolean;
  isSale?: boolean;
  stock: number;
}

// Transform API product to our app's product format
const transformProduct = (product: ApiProduct): FormattedProduct => {
  // Randomly assign some products as new or on sale
  const isNew = Math.random() > 0.7;
  const isSale = Math.random() > 0.8;
  const salePrice = isSale ? Number((product.price * 0.8).toFixed(2)) : undefined;
  
  // Generate random features based on the product category
  const generateFeatures = (category: string): string[] => {
    const baseFeatures = [
      `Premium ${category} product`,
      'High quality materials',
      'Exceptional craftsmanship'
    ];
    
    const categoryFeatures: Record<string, string[]> = {
      'electronics': [
        'Energy efficient',
        'Smart connectivity',
        'Extended warranty available',
        'Plug and play setup'
      ],
      'jewelery': [
        'Ethically sourced materials',
        'Tarnish resistant',
        'Gift box included',
        'Certified authenticity'
      ],
      'men\'s clothing': [
        'Machine washable',
        'Breathable fabric',
        'Comfortable fit',
        'Durable construction'
      ],
      'women\'s clothing': [
        'Versatile styling options',
        'Comfortable all-day wear',
        'Easy care instructions',
        'Seasonal must-have'
      ]
    };
    
    const specificFeatures = categoryFeatures[category] || [];
    
    // Return a combination of base features and category-specific features
    return [...baseFeatures, ...specificFeatures.slice(0, 2)];
  };

  return {
    id: product.id.toString(),
    name: product.title,
    description: product.description,
    price: product.price,
    salePrice,
    category: product.category,
    image: product.image,
    rating: product.rating.rate,
    reviewCount: product.rating.count,
    features: generateFeatures(product.category),
    isNew,
    isSale,
    stock: Math.floor(Math.random() * 50) + 5 // Random stock between 5-55
  };
};

// Fetch all products
export const fetchProducts = async (): Promise<FormattedProduct[]> => {
  try {
    const response = await fetch(`${API_URL}/products`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch products');
    }
    
    const data: ApiProduct[] = await response.json();
    return data.map(transformProduct);
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};

// Fetch a single product by ID
export const fetchProductById = async (id: string): Promise<FormattedProduct> => {
  try {
    const response = await fetch(`${API_URL}/products/${id}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch product with id ${id}`);
    }
    
    const data: ApiProduct = await response.json();
    return transformProduct(data);
  } catch (error) {
    console.error(`Error fetching product ${id}:`, error);
    throw error;
  }
};

// Fetch products by category
export const fetchProductsByCategory = async (category: string): Promise<FormattedProduct[]> => {
  try {
    const response = await fetch(`${API_URL}/products/category/${category}`);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch products in category ${category}`);
    }
    
    const data: ApiProduct[] = await response.json();
    return data.map(transformProduct);
  } catch (error) {
    console.error(`Error fetching products in category ${category}:`, error);
    throw error;
  }
};

// Get all categories
export const fetchCategories = async (): Promise<string[]> => {
  try {
    const response = await fetch(`${API_URL}/products/categories`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch categories');
    }
    
    const data: string[] = await response.json();
    return data.map(category => 
      category.charAt(0).toUpperCase() + category.slice(1).replace(/'/g, '')
    );
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
};
