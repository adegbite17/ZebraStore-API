
export interface Product {
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

export const products: Product[] = [
  {
    id: '1',
    name: 'Wireless Noise Cancelling Headphones',
    description: 'Experience crystal-clear audio with our premium noise cancelling headphones. Perfect for travel, work, or relaxing at home.',
    price: 299.99,
    category: 'Electronics',
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e',
    rating: 4.8,
    reviewCount: 423,
    features: [
      'Active noise cancellation',
      'Up to 30 hours battery life',
      'Bluetooth 5.0 connectivity',
      'Built-in microphone for calls',
      'Premium comfort with memory foam ear cups'
    ],
    colors: ['Black', 'Silver', 'Blue'],
    isNew: true,
    stock: 25
  },
  {
    id: '2',
    name: 'Ultra HD Smart TV 55"',
    description: 'Immerse yourself in stunning 4K resolution with this smart TV featuring the latest technology for an exceptional viewing experience.',
    price: 799.99,
    salePrice: 649.99,
    category: 'Electronics',
    image: 'https://images.unsplash.com/photo-1567690187548-f07b1d7bf5a9',
    rating: 4.5,
    reviewCount: 287,
    features: [
      '4K Ultra HD resolution',
      'Smart TV functionality',
      'Multiple HDMI and USB ports',
      'Built-in streaming apps',
      'Voice control compatibility'
    ],
    isSale: true,
    stock: 12
  },
  {
    id: '3',
    name: 'Premium Leather Backpack',
    description: 'Handcrafted from full-grain leather, this stylish backpack combines durability with sophisticated design for everyday use.',
    price: 159.99,
    category: 'Fashion',
    image: 'https://images.unsplash.com/photo-1491637639811-60e2756cc1c7',
    rating: 4.7,
    reviewCount: 156,
    features: [
      'Genuine full-grain leather',
      'Laptop compartment fits up to 15" devices',
      'Multiple internal organization pockets',
      'Water-resistant lining',
      'Adjustable padded shoulder straps'
    ],
    colors: ['Brown', 'Black', 'Tan'],
    stock: 45
  },
  {
    id: '4',
    name: 'Smart Fitness Watch',
    description: 'Track your health and fitness goals with this advanced smartwatch featuring heart rate monitoring, GPS, and personalized coaching.',
    price: 199.99,
    category: 'Electronics',
    image: 'https://images.unsplash.com/photo-1546868871-7041f2a55e12',
    rating: 4.4,
    reviewCount: 319,
    features: [
      '24/7 heart rate monitoring',
      'Built-in GPS tracking',
      'Water-resistant to 50m',
      'Sleep analysis',
      '7-day battery life'
    ],
    colors: ['Black', 'White', 'Blue'],
    isNew: true,
    stock: 38
  },
  {
    id: '5',
    name: 'Professional Blender',
    description: 'A powerful blender for smoothies, soups, and more. Features multiple speed settings and durable stainless steel blades.',
    price: 129.99,
    salePrice: 99.99,
    category: 'Home & Kitchen',
    image: 'https://images.unsplash.com/photo-1507914997799-d84c8561d15c',
    rating: 4.6,
    reviewCount: 203,
    features: [
      '1000W motor',
      'Variable speed control',
      'Pulse function',
      '64oz BPA-free container',
      'Dishwasher-safe parts'
    ],
    isSale: true,
    stock: 15
  },
  {
    id: '6',
    name: 'Designer Sunglasses',
    description: 'Protect your eyes in style with these premium UV-protected sunglasses featuring a timeless design that complements any outfit.',
    price: 149.99,
    category: 'Fashion',
    image: 'https://images.unsplash.com/photo-1511499767150-a48a237f0083',
    rating: 4.3,
    reviewCount: 127,
    features: [
      'Polarized lenses',
      'Full UV protection',
      'Lightweight frame',
      'Anti-reflective coating',
      'Includes protective case'
    ],
    colors: ['Black', 'Tortoise', 'Gold'],
    stock: 52
  },
  {
    id: '7',
    name: 'Wireless Gaming Mouse',
    description: 'Dominate your games with this high-precision wireless gaming mouse featuring customizable RGB lighting and programmable buttons.',
    price: 79.99,
    category: 'Electronics',
    image: 'https://images.unsplash.com/photo-1563297007-0686b7003af7',
    rating: 4.7,
    reviewCount: 318,
    features: [
      '16,000 DPI optical sensor',
      'Ultra-fast 1ms response time',
      'RGB customizable lighting',
      '8 programmable buttons',
      'Rechargeable battery with 60hr life'
    ],
    isNew: true,
    stock: 30
  },
  {
    id: '8',
    name: 'Premium Coffee Maker',
    description: 'Brew barista-quality coffee at home with this programmable coffee maker featuring precision temperature control and a built-in grinder.',
    price: 199.99,
    salePrice: 159.99,
    category: 'Home & Kitchen',
    image: 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085',
    rating: 4.5,
    reviewCount: 165,
    features: [
      'Built-in conical burr grinder',
      'Programmable 24-hour timer',
      'Adjustable brew strength',
      'Thermal carafe keeps coffee hot for hours',
      'Water filtration system'
    ],
    isSale: true,
    stock: 8
  }
];

export const getProducts = (params?: {
  category?: string;
  isNew?: boolean;
  isSale?: boolean;
  search?: string;
}) => {
  let filteredProducts = [...products];

  if (params?.category) {
    filteredProducts = filteredProducts.filter(
      (product) => product.category.toLowerCase() === params.category?.toLowerCase()
    );
  }

  if (params?.isNew) {
    filteredProducts = filteredProducts.filter((product) => product.isNew);
  }

  if (params?.isSale) {
    filteredProducts = filteredProducts.filter((product) => product.isSale);
  }

  if (params?.search) {
    const searchLower = params.search.toLowerCase();
    filteredProducts = filteredProducts.filter(
      (product) =>
        product.name.toLowerCase().includes(searchLower) ||
        product.description.toLowerCase().includes(searchLower) ||
        product.category.toLowerCase().includes(searchLower)
    );
  }

  return filteredProducts;
};

export const getProductById = (id: string) => {
  return products.find((product) => product.id === id);
};

export const getRelatedProducts = (id: string, category: string, limit = 4) => {
  return products
    .filter((product) => product.id !== id && product.category === category)
    .slice(0, limit);
};
