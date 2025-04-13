
import { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  SimpleGrid,
  Image,
  Flex,
  Stack,
  VStack,
  HStack,
  Badge,
  useColorModeValue,
  Link,
  Icon,
  Spinner,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { ArrowRightIcon, TruckIcon, ShieldCheckIcon, RefreshCwIcon } from 'lucide-react';
import ProductCard from '../components/product/ProductCard';
import { fetchProducts, fetchCategories, FormattedProduct } from '../services/api';

const HomePage = () => {
  const [products, setProducts] = useState<FormattedProduct[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [productsData, categoriesData] = await Promise.all([
          fetchProducts(),
          fetchCategories()
        ]);
        
        setProducts(productsData);
        setCategories(categoriesData);
        setError(null);
      } catch (err) {
        setError('Failed to load products. Please refresh the page to try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, []);

  const getFeaturedProducts = () => products.slice(0, 4);
  const getNewArrivals = () => products.filter(p => p.isNew).slice(0, 4);
  const getSaleProducts = () => products.filter(p => p.isSale).slice(0, 4);

  // Prepare category images for display
  const categoryImages = [
    { name: 'Electronics', image: 'https://images.unsplash.com/photo-1550009158-9ebf69173e03' },
    { name: "Men's Clothing", image: 'https://images.unsplash.com/photo-1552831388-6a0b3575b32a' },
    { name: "Women's Clothing", image: 'https://images.unsplash.com/photo-1551232864-3f0890e580d9' },
    { name: 'Jewelery', image: 'https://images.unsplash.com/photo-1506630448388-4e683c67ddb0' },
  ];

  // Match API categories with our images or use default
  const displayCategories = categories.map(category => {
    const foundImage = categoryImages.find(img => 
      img.name.toLowerCase() === category.toLowerCase()
    );
    return {
      name: category,
      image: foundImage ? foundImage.image : 'https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da',
      link: `/products?category=${category}`,
    };
  }).slice(0, 3); // Limit to 3 categories

  if (loading) {
    return (
      <Flex justify="center" align="center" minH="60vh" direction="column">
        <Spinner size="xl" color="brand.500" thickness="4px" mb={4} />
        <Text>Loading amazing products for you...</Text>
      </Flex>
    );
  }

  if (error) {
    return (
      <Container maxW="container.xl" py={12}>
        <Alert
          status="error"
          variant="subtle"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          textAlign="center"
          height="200px"
          borderRadius="md"
        >
          <AlertIcon boxSize="40px" mr={0} />
          <Text mt={4} mb={1} fontSize="lg">
            {error}
          </Text>
          <Button 
            colorScheme="brand" 
            mt={4}
            onClick={() => window.location.reload()}
          >
            Refresh Page
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Box>
      {/* Hero Section */}
      <Box
        bg={useColorModeValue('gray.50', 'gray.900')}
        position="relative"
        h={{ base: '500px', md: '600px' }}
        overflow="hidden"
      >
        <Image
          src="https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da"
          alt="Shopping hero"
          objectFit="cover"
          objectPosition="center"
          h="100%"
          w="100%"
        />
        <Box
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          bg="blackAlpha.600"
          zIndex="1"
        />
        <Container maxW="container.xl" centerContent zIndex="2" position="relative" h="100%">
          <VStack
            spacing={5}
            alignItems={{ base: 'center', md: 'flex-start' }}
            justify="center"
            h="100%"
            textAlign={{ base: 'center', md: 'left' }}
            color="white"
            px={4}
          >
            <Badge colorScheme="brand" px={3} py={1} rounded="full" fontSize="sm">
              New Season Collection
            </Badge>
            <Heading
              as="h1"
              fontSize={{ base: '3xl', md: '4xl', lg: '5xl' }}
              fontWeight="bold"
              lineHeight="shorter"
            >
              Discover Stylish Finds <br />
              For Every Occasion
            </Heading>
            <Text fontSize={{ base: 'md', md: 'lg' }} maxW="600px">
              Shop the latest trends and discover premium quality products with 
              fast delivery and exceptional customer service.
            </Text>
            <HStack spacing={4} mt={2}>
              <Button
                as={RouterLink}
                to="/products"
                colorScheme="brand"
                size="lg"
                bg="brand.500"
                _hover={{ bg: 'brand.600' }}
                rightIcon={<ArrowRightIcon size={16} />}
                boxShadow="lg"
              >
                Shop Now
              </Button>
              <Button
                as={RouterLink}
                to="/products?new=true"
                variant="outline"
                size="lg"
                color="white"
                _hover={{ bg: 'whiteAlpha.200' }}
                borderColor="white"
              >
                New Arrivals
              </Button>
            </HStack>
          </VStack>
        </Container>
      </Box>

      {/* Categories Section */}
      <Container maxW="container.xl" py={16}>
        <VStack spacing={8}>
          <Heading as="h2" fontSize="3xl" textAlign="center">
            Shop by Category
          </Heading>
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={8} w="full">
            {displayCategories.map((category) => (
              <Box
                key={category.name}
                as={RouterLink}
                to={category.link}
                position="relative"
                h="250px"
                overflow="hidden"
                borderRadius="xl"
                boxShadow="lg"
                transition="all 0.3s"
                _hover={{ transform: 'scale(1.02)' }}
              >
                <Image
                  src={category.image}
                  alt={category.name}
                  objectFit="cover"
                  w="100%"
                  h="100%"
                />
                <Box
                  position="absolute"
                  bottom="0"
                  w="100%"
                  bg="blackAlpha.700"
                  p={4}
                  color="white"
                >
                  <Heading size="md">{category.name}</Heading>
                </Box>
              </Box>
            ))}
          </SimpleGrid>
        </VStack>
      </Container>

      {/* Featured Products */}
      <Box bg={useColorModeValue('gray.50', 'gray.900')} py={16}>
        <Container maxW="container.xl">
          <Flex
            justify="space-between"
            align="center"
            mb={8}
            direction={{ base: 'column', sm: 'row' }}
            gap={4}
          >
            <Heading as="h2" fontSize="3xl">
              Featured Products
            </Heading>
            <Button
              as={RouterLink}
              to="/products"
              variant="outline"
              colorScheme="brand"
              rightIcon={<ArrowRightIcon size={16} />}
            >
              View All Products
            </Button>
          </Flex>

          <SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} spacing={6}>
            {getFeaturedProducts().map((product) => (
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
        </Container>
      </Box>

      {/* New Arrivals */}
      <Container maxW="container.xl" py={16}>
        <Flex
          justify="space-between"
          align="center"
          mb={8}
          direction={{ base: 'column', sm: 'row' }}
          gap={4}
        >
          <Heading as="h2" fontSize="3xl">
            New Arrivals
          </Heading>
          <Button
            as={RouterLink}
            to="/products?new=true"
            variant="outline"
            colorScheme="brand"
            rightIcon={<ArrowRightIcon size={16} />}
          >
            View All New Items
          </Button>
        </Flex>

        <SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} spacing={6}>
          {getNewArrivals().map((product) => (
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
      </Container>

      {/* Special Offer Banner */}
      <Box
        bg={useColorModeValue('brand.500', 'brand.600')}
        color="white"
        py={10}
        position="relative"
        overflow="hidden"
      >
        <Container maxW="container.xl">
          <Flex
            direction={{ base: 'column', md: 'row' }}
            align="center"
            justify="space-between"
            gap={8}
          >
            <VStack align={{ base: 'center', md: 'flex-start' }} spacing={4}>
              <Heading as="h2" fontSize={{ base: '2xl', md: '3xl' }}>
                Special Summer Sale
              </Heading>
              <Text fontSize="lg">
                Get up to 40% off on selected items. Limited time offer!
              </Text>
              <Button
                as={RouterLink}
                to="/products?sale=true"
                bg="white"
                color="brand.500"
                size="lg"
                _hover={{ bg: 'gray.100' }}
                mt={2}
                boxShadow="md"
              >
                Shop the Sale
              </Button>
            </VStack>
            <Box
              position={{ base: 'relative', md: 'absolute' }}
              right={{ md: '50px' }}
              bottom={{ md: '-20px' }}
              width={{ base: '100%', md: 'auto' }}
              height={{ base: '200px', md: 'auto' }}
            >
              <Image
                src="https://images.unsplash.com/photo-1607082348566-187342175e2f"
                alt="Sale Banner"
                objectFit="contain"
                maxH="250px"
                mx="auto"
              />
            </Box>
          </Flex>
        </Container>
      </Box>

      {/* Why Choose Us */}
      <Container maxW="container.xl" py={16}>
        <VStack spacing={10}>
          <Heading as="h2" fontSize="3xl" textAlign="center">
            Why Shop With Us
          </Heading>
          
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10}>
            <VStack spacing={4} align="center" textAlign="center">
              <Flex
                align="center"
                justify="center"
                bg={useColorModeValue('brand.50', 'gray.700')}
                rounded="full"
                w="80px"
                h="80px"
                mb={2}
              >
                <Icon as={TruckIcon} boxSize={8} color="brand.500" />
              </Flex>
              <Heading as="h3" size="md">
                Free & Fast Shipping
              </Heading>
              <Text color={useColorModeValue('gray.600', 'gray.400')}>
                Free shipping on all orders over $50, and same-day dispatch on orders placed before 2pm.
              </Text>
            </VStack>

            <VStack spacing={4} align="center" textAlign="center">
              <Flex
                align="center"
                justify="center"
                bg={useColorModeValue('brand.50', 'gray.700')}
                rounded="full"
                w="80px"
                h="80px"
                mb={2}
              >
                <Icon as={ShieldCheckIcon} boxSize={8} color="brand.500" />
              </Flex>
              <Heading as="h3" size="md">
                Secure Payments
              </Heading>
              <Text color={useColorModeValue('gray.600', 'gray.400')}>
                All payments are processed securely using the latest encryption technology.
              </Text>
            </VStack>

            <VStack spacing={4} align="center" textAlign="center">
              <Flex
                align="center"
                justify="center"
                bg={useColorModeValue('brand.50', 'gray.700')}
                rounded="full"
                w="80px"
                h="80px"
                mb={2}
              >
                <Icon as={RefreshCwIcon} boxSize={8} color="brand.500" />
              </Flex>
              <Heading as="h3" size="md">
                Easy Returns
              </Heading>
              <Text color={useColorModeValue('gray.600', 'gray.400')}>
                Not happy with your purchase? Return within 30 days for a full refund, no questions asked.
              </Text>
            </VStack>
          </SimpleGrid>
        </VStack>
      </Container>
    </Box>
  );
};

export default HomePage;
