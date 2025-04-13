
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Box,
  Container,
  Heading,
  SimpleGrid,
  Flex,
  Select,
  Input,
  Text,
  Stack,
  Checkbox,
  Button,
  Badge,
  useColorModeValue,
  Icon,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useDisclosure,
  RangeSlider,
  RangeSliderTrack,
  RangeSliderFilledTrack,
  RangeSliderThumb,
  InputGroup,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { Menu, Search, X, RefreshCw } from 'lucide-react';
import ProductCard from '../components/product/ProductCard';
import { fetchProducts, fetchCategories, FormattedProduct } from '../services/api';

const ProductsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [products, setProducts] = useState<FormattedProduct[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<FormattedProduct[]>([]);
  const [categories, setCategories] = useState<string[]>(['All']);
  const [selectedCategory, setSelectedCategory] = useState<string>(searchParams.get('category') || 'All');
  const [showNew, setShowNew] = useState<boolean>(searchParams.get('new') === 'true');
  const [showSale, setShowSale] = useState<boolean>(searchParams.get('sale') === 'true');
  const [searchQuery, setSearchQuery] = useState<string>(searchParams.get('search') || '');
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 1000]);
  const [sortOption, setSortOption] = useState<string>('featured');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // Fetch categories first
        const categoriesData = await fetchCategories();
        setCategories(['All', ...categoriesData]);
        
        // Then fetch products
        const productsData = await fetchProducts();
        setProducts(productsData);
        
        // Set initial price range based on products
        if (productsData.length > 0) {
          const minPrice = Math.floor(Math.min(...productsData.map(p => p.price)));
          const maxPrice = Math.ceil(Math.max(...productsData.map(p => p.price)));
          setPriceRange([minPrice, maxPrice]);
        }
        
        setError(null);
      } catch (err) {
        setError('Failed to load products. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, []);

  useEffect(() => {
    // Skip filtering if products haven't loaded yet
    if (loading || products.length === 0) return;
    
    // Update search params
    const params: Record<string, string> = {};
    if (selectedCategory !== 'All') params.category = selectedCategory;
    if (showNew) params.new = 'true';
    if (showSale) params.sale = 'true';
    if (searchQuery) params.search = searchQuery;
    setSearchParams(params);

    // Filter products
    let result = [...products];

    if (selectedCategory !== 'All') {
      result = result.filter(
        product => product.category.toLowerCase() === selectedCategory.toLowerCase()
      );
    }

    if (showNew) {
      result = result.filter(product => product.isNew);
    }

    if (showSale) {
      result = result.filter(product => product.isSale);
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        product =>
          product.name.toLowerCase().includes(query) ||
          product.description.toLowerCase().includes(query) ||
          product.category.toLowerCase().includes(query)
      );
    }

    result = result.filter(
      product => product.price >= priceRange[0] && product.price <= priceRange[1]
    );

    // Sort products
    switch (sortOption) {
      case 'price-asc':
        result.sort((a, b) => a.price - b.price);
        break;
      case 'price-desc':
        result.sort((a, b) => b.price - a.price);
        break;
      case 'rating':
        result.sort((a, b) => b.rating - a.rating);
        break;
      case 'newest':
        result = result.filter(p => p.isNew).concat(result.filter(p => !p.isNew));
        break;
      default:
        // Default sorting (featured)
        break;
    }

    setFilteredProducts(result);
  }, [selectedCategory, showNew, showSale, searchQuery, priceRange, sortOption, products, setSearchParams, loading]);

  const resetFilters = () => {
    setSelectedCategory('All');
    setShowNew(false);
    setShowSale(false);
    setSearchQuery('');
    if (products.length > 0) {
      const minPrice = Math.floor(Math.min(...products.map(p => p.price)));
      const maxPrice = Math.ceil(Math.max(...products.map(p => p.price)));
      setPriceRange([minPrice, maxPrice]);
    } else {
      setPriceRange([0, 1000]);
    }
    setSortOption('featured');
  };

  const handleRetry = async () => {
    try {
      setLoading(true);
      setError(null);
      const productsData = await fetchProducts();
      setProducts(productsData);
    } catch (err) {
      setError('Failed to load products. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const FilterSidebar = () => (
    <Stack spacing={6}>
      <Box>
        <Heading size="md" mb={3}>
          Categories
        </Heading>
        {categories.map((category) => (
          <Checkbox
            key={category}
            isChecked={selectedCategory === category}
            onChange={() => setSelectedCategory(category)}
            mb={2}
            colorScheme="brand"
          >
            {category}
          </Checkbox>
        ))}
      </Box>

      <Box>
        <Heading size="md" mb={3}>
          Price Range
        </Heading>
        <RangeSlider
          min={0}
          max={1000}
          step={10}
          value={priceRange}
          onChange={(val) => setPriceRange([val[0], val[1]])}
          mb={4}
          colorScheme="brand"
        >
          <RangeSliderTrack>
            <RangeSliderFilledTrack />
          </RangeSliderTrack>
          <RangeSliderThumb index={0} />
          <RangeSliderThumb index={1} />
        </RangeSlider>
        <Flex justify="space-between">
          <Text>${priceRange[0]}</Text>
          <Text>${priceRange[1]}</Text>
        </Flex>
      </Box>

      <Box>
        <Heading size="md" mb={3}>
          Filter By
        </Heading>
        <Stack spacing={2}>
          <Checkbox isChecked={showNew} onChange={(e) => setShowNew(e.target.checked)} colorScheme="brand">
            New Arrivals
          </Checkbox>
          <Checkbox isChecked={showSale} onChange={(e) => setShowSale(e.target.checked)} colorScheme="brand">
            On Sale
          </Checkbox>
        </Stack>
      </Box>

      <Button
        leftIcon={<Icon as={X} />}
        variant="outline"
        onClick={resetFilters}
        mt={2}
        colorScheme="brand"
      >
        Reset Filters
      </Button>
    </Stack>
  );

  return (
    <Container maxW="container.xl" py={8}>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading as="h1" size="xl">
          Products
          {(selectedCategory !== 'All' || showNew || showSale) && (
            <Badge ml={2} colorScheme="brand" fontSize="sm">
              Filtered
            </Badge>
          )}
        </Heading>
        <Button
          leftIcon={<Icon as={Menu} />}
          display={{ base: 'flex', md: 'none' }}
          onClick={onOpen}
          colorScheme="brand"
        >
          Filters
        </Button>
      </Flex>

      <Flex gap={8} direction={{ base: 'column', md: 'row' }}>
        {/* Filters - Desktop */}
        <Box
          w={{ base: 'full', md: '250px' }}
          display={{ base: 'none', md: 'block' }}
          p={6}
          bg={bgColor}
          borderWidth="1px"
          borderColor={borderColor}
          borderRadius="xl"
          position="sticky"
          top="100px"
          alignSelf="flex-start"
          boxShadow="sm"
        >
          <FilterSidebar />
        </Box>

        {/* Filters - Mobile */}
        <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
          <DrawerOverlay />
          <DrawerContent>
            <DrawerCloseButton />
            <DrawerHeader borderBottomWidth="1px">Filters</DrawerHeader>
            <DrawerBody>
              <FilterSidebar />
            </DrawerBody>
          </DrawerContent>
        </Drawer>

        <Box flex="1">
          {/* Search and Sort */}
          <Flex
            mb={6}
            direction={{ base: 'column', sm: 'row' }}
            align={{ sm: 'center' }}
            justify="space-between"
            gap={4}
          >
            <Flex
              as="form"
              onSubmit={(e) => {
                e.preventDefault();
              }}
              maxW={{ base: 'full', sm: '320px' }}
              flex={{ sm: 1 }}
            >
              <InputGroup>
                <Input
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  pr="10"
                  borderRadius="md"
                  focusBorderColor="brand.500"
                />
                <Box position="absolute" right="4" top="3">
                  <Search size={16} />
                </Box>
              </InputGroup>
            </Flex>

            <Select
              value={sortOption}
              onChange={(e) => setSortOption(e.target.value)}
              maxW={{ base: 'full', sm: '180px' }}
              borderRadius="md"
              focusBorderColor="brand.500"
            >
              <option value="featured">Featured</option>
              <option value="price-asc">Price: Low to High</option>
              <option value="price-desc">Price: High to Low</option>
              <option value="rating">Highest Rated</option>
              <option value="newest">Newest</option>
            </Select>
          </Flex>

          {/* Loading or Error State */}
          {loading && (
            <Flex direction="column" align="center" justify="center" py={10}>
              <Spinner size="xl" color="brand.500" thickness="4px" mb={4} />
              <Text>Loading products...</Text>
            </Flex>
          )}

          {error && (
            <Alert
              status="error"
              variant="subtle"
              flexDirection="column"
              alignItems="center"
              justifyContent="center"
              textAlign="center"
              height="200px"
              borderRadius="md"
              mb={6}
            >
              <AlertIcon boxSize="40px" mr={0} />
              <AlertTitle mt={4} mb={1} fontSize="lg">
                Failed to load products
              </AlertTitle>
              <AlertDescription maxWidth="sm" mb={4}>
                {error}
              </AlertDescription>
              <Button
                leftIcon={<RefreshCw size={16} />}
                colorScheme="brand"
                onClick={handleRetry}
              >
                Try Again
              </Button>
            </Alert>
          )}

          {/* Product Count */}
          {!loading && !error && (
            <Text mb={4} color="gray.600">
              Showing {filteredProducts.length} products
            </Text>
          )}

          {/* Products Grid */}
          {!loading && !error && filteredProducts.length > 0 ? (
            <SimpleGrid columns={{ base: 1, sm: 2, md: 3, lg: 3 }} spacing={6}>
              {filteredProducts.map((product) => (
                <ProductCard
                  key={product.id}
                  id={product.id}
                  name={product.name}
                  category={product.category}
                  image={product.image}
                  price={product.price}
                  rating={product.rating}
                  reviewCount={product.reviewCount}
                  isNew={product.isNew}
                  isSale={product.isSale}
                  salePrice={product.salePrice}
                />
              ))}
            </SimpleGrid>
          ) : !loading && !error ? (
            <Flex
              direction="column"
              align="center"
              justify="center"
              py={10}
              bg={bgColor}
              borderRadius="xl"
              borderWidth="1px"
              borderColor={borderColor}
              boxShadow="sm"
            >
              <Icon as={Search} boxSize={12} mb={4} color="gray.400" />
              <Heading size="md" mb={2}>
                No products found
              </Heading>
              <Text color="gray.500" mb={4} textAlign="center">
                We couldn't find any products matching your current filters.
              </Text>
              <Button onClick={resetFilters} colorScheme="brand">Reset Filters</Button>
            </Flex>
          ) : null}
        </Box>
      </Flex>
    </Container>
  );
};

export default ProductsPage;
