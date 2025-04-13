
import { useEffect, useState } from 'react';
import { useParams, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Container,
  Heading,
  Text,
  Image,
  Button,
  Flex,
  Grid,
  GridItem,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  Badge,
  Stack,
  HStack,
  Divider,
  Tab,
  Tabs,
  TabList,
  TabPanel,
  TabPanels,
  useToast,
  Skeleton,
  VStack,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { ChevronRightIcon, StarIcon, RefreshCw } from 'lucide-react';
import { fetchProductById, FormattedProduct } from '../services/api';
import { useCart } from '../context/CartContext';

const ProductDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<FormattedProduct | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);
  const { addItem } = useCart();
  const toast = useToast();

  useEffect(() => {
    const loadProduct = async () => {
      if (!id) return;
      
      try {
        setLoading(true);
        setError(null);
        const productData = await fetchProductById(id);
        setProduct(productData);
      } catch (err) {
        setError('Failed to load product details. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    loadProduct();
    // Scroll to top on page load
    window.scrollTo(0, 0);
  }, [id]);

  const handleRetry = async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      setError(null);
      const productData = await fetchProductById(id);
      setProduct(productData);
    } catch (err) {
      setError('Failed to load product details. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = () => {
    if (product) {
      addItem({
        id: product.id,
        name: product.name,
        price: product.isSale && product.salePrice ? product.salePrice : product.price,
        image: product.image,
      });
      
      toast({
        title: 'Added to cart',
        description: `${product.name} has been added to your cart`,
        status: 'success',
        duration: 3000,
        isClosable: true,
        position: 'top-right',
      });
    }
  };

  if (loading) {
    return (
      <Container maxW="container.xl" py={8}>
        <Breadcrumb separator={<ChevronRightIcon size={14} />} mb={8}>
          <BreadcrumbItem>
            <BreadcrumbLink as={RouterLink} to="/">Home</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem>
            <BreadcrumbLink as={RouterLink} to="/products">Products</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem isCurrentPage>
            <BreadcrumbLink>Loading...</BreadcrumbLink>
          </BreadcrumbItem>
        </Breadcrumb>
        
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={8}>
          <GridItem>
            <Skeleton height="400px" borderRadius="xl" />
          </GridItem>
          <GridItem>
            <Stack spacing={4}>
              <Skeleton height="40px" width="70%" />
              <Skeleton height="20px" width="40%" />
              <Skeleton height="30px" width="30%" />
              <Skeleton height="100px" />
              <Skeleton height="40px" width="180px" />
            </Stack>
          </GridItem>
        </Grid>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxW="container.xl" py={8}>
        <Breadcrumb separator={<ChevronRightIcon size={14} />} mb={8}>
          <BreadcrumbItem>
            <BreadcrumbLink as={RouterLink} to="/">Home</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem>
            <BreadcrumbLink as={RouterLink} to="/products">Products</BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbItem isCurrentPage>
            <BreadcrumbLink>Error</BreadcrumbLink>
          </BreadcrumbItem>
        </Breadcrumb>
        
        <Alert
          status="error"
          variant="subtle"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          textAlign="center"
          height="300px"
          borderRadius="xl"
        >
          <AlertIcon boxSize="40px" mr={0} />
          <AlertTitle mt={4} mb={1} fontSize="lg">
            Product Not Found
          </AlertTitle>
          <AlertDescription maxWidth="sm" mb={4}>
            {error}
          </AlertDescription>
          <HStack spacing={4}>
            <Button
              leftIcon={<RefreshCw size={16} />}
              colorScheme="brand"
              onClick={handleRetry}
            >
              Try Again
            </Button>
            <Button 
              as={RouterLink} 
              to="/products" 
              variant="outline"
              colorScheme="brand"
            >
              Back to Products
            </Button>
          </HStack>
        </Alert>
      </Container>
    );
  }

  if (!product) {
    return (
      <Container maxW="container.xl" py={8}>
        <Heading>Product Not Found</Heading>
        <Text mt={4}>The product you're looking for does not exist.</Text>
        <Button as={RouterLink} to="/products" colorScheme="brand" mt={6}>
          Return to Products
        </Button>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <Breadcrumb separator={<ChevronRightIcon size={14} />} mb={8}>
        <BreadcrumbItem>
          <BreadcrumbLink as={RouterLink} to="/">Home</BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbItem>
          <BreadcrumbLink as={RouterLink} to="/products">Products</BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbItem isCurrentPage>
          <BreadcrumbLink>{product.name}</BreadcrumbLink>
        </BreadcrumbItem>
      </Breadcrumb>
      
      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={8}>
        <GridItem>
          <Box 
            borderRadius="xl" 
            overflow="hidden" 
            bg="white"
            boxShadow="lg"
            p={8}
            display="flex"
            justifyContent="center"
            alignItems="center"
            height="500px"
          >
            <Image 
              src={product.image}
              alt={product.name}
              maxH="400px"
              objectFit="contain"
            />
          </Box>
        </GridItem>
        
        <GridItem>
          <Box bg="white" p={8} borderRadius="xl" boxShadow="md" height="100%">
            <Stack spacing={6}>
              <Box>
                <HStack>
                  <Badge colorScheme="purple" px={2} py={1} borderRadius="full">{product.category}</Badge>
                  {product.isNew && <Badge colorScheme="green" px={2} py={1} borderRadius="full">New</Badge>}
                  {product.isSale && <Badge colorScheme="red" px={2} py={1} borderRadius="full">Sale</Badge>}
                </HStack>
                <Heading size="xl" mt={3}>{product.name}</Heading>
              </Box>
              
              <HStack>
                <HStack>
                  {Array(5)
                    .fill('')
                    .map((_, i) => (
                      <StarIcon
                        key={i}
                        color={i < Math.floor(product.rating) ? 'brand.500' : 'gray.300'}
                        size={16}
                      />
                    ))
                  }
                  <Text ml={1} fontSize="sm" color="gray.600">
                    ({product.reviewCount} reviews)
                  </Text>
                </HStack>
              </HStack>
              
              <Box>
                {product.isSale && product.salePrice ? (
                  <HStack>
                    <Text
                      fontSize="2xl"
                      fontWeight="bold"
                      color="brand.500"
                    >
                      ${product.salePrice.toFixed(2)}
                    </Text>
                    <Text
                      fontSize="lg"
                      fontWeight="medium"
                      color="gray.500"
                      textDecoration="line-through"
                    >
                      ${product.price.toFixed(2)}
                    </Text>
                    <Badge colorScheme="red" ml={2}>
                      {Math.round((1 - product.salePrice / product.price) * 100)}% OFF
                    </Badge>
                  </HStack>
                ) : (
                  <Text
                    fontSize="2xl"
                    fontWeight="bold"
                    color="brand.500"
                  >
                    ${product.price.toFixed(2)}
                  </Text>
                )}
              </Box>
              
              <Text color="gray.700">{product.description}</Text>
              
              <Box>
                <Heading size="sm" mb={2}>Key Features:</Heading>
                <VStack align="stretch" spacing={1}>
                  {product.features.map((feature, index) => (
                    <HStack key={index} alignItems="flex-start">
                      <Box as="span" color="brand.500" fontWeight="bold" mt={1}>•</Box>
                      <Text>{feature}</Text>
                    </HStack>
                  ))}
                </VStack>
              </Box>
              
              <Divider />
              
              <HStack spacing={4}>
                <Button 
                  onClick={handleAddToCart}
                  colorScheme="brand"
                  size="lg"
                  w="full"
                  borderRadius="md"
                  boxShadow="md"
                  _hover={{ transform: 'translateY(-2px)', boxShadow: 'lg' }}
                  transition="all 0.2s"
                >
                  Add to Cart
                </Button>
              </HStack>
              
              <Box bg="gray.50" p={4} borderRadius="md" mt={2}>
                <HStack>
                  <Box color="brand.500">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M3 3H5L5.4 5M5.4 5H21L17 13H7M5.4 5L7 13M7 13L4.707 15.293C4.077 15.923 4.523 17 5.414 17H17M17 17C16.4696 17 15.9609 17.2107 15.5858 17.5858C15.2107 17.9609 15 18.4696 15 19C15 19.5304 15.2107 20.0391 15.5858 20.4142C15.9609 20.7893 16.4696 21 17 21C17.5304 21 18.0391 20.7893 18.4142 20.4142C18.7893 20.0391 19 19.5304 19 19C19 18.4696 18.7893 17.9609 18.4142 17.5858C18.0391 17.2107 17.5304 17 17 17Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </Box>
                  <Text fontWeight="medium">Free shipping on orders over $50</Text>
                </HStack>
              </Box>
            </Stack>
          </Box>
        </GridItem>
      </Grid>
      
      <Box mt={12} bg="white" borderRadius="xl" boxShadow="md" overflow="hidden">
        <Tabs colorScheme="brand" p={4}>
          <TabList>
            <Tab fontWeight="semibold">Description</Tab>
            <Tab fontWeight="semibold">Details</Tab>
            <Tab fontWeight="semibold">Reviews</Tab>
          </TabList>
          <TabPanels>
            <TabPanel>
              <Text>{product.description}</Text>
              <Text mt={4}>
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam 
                auctor, nisl eget ultricies lacinia, nisl nisl aliquam nisl, eget
                aliquam nisl nisl eget nisl. Nullam auctor, nisl eget ultricies 
                lacinia, nisl nisl aliquam nisl, eget aliquam nisl nisl eget nisl.
              </Text>
            </TabPanel>
            <TabPanel>
              <Stack spacing={4}>
                <HStack>
                  <Text fontWeight="bold" w="200px">Category:</Text>
                  <Text>{product.category}</Text>
                </HStack>
                <HStack>
                  <Text fontWeight="bold" w="200px">Rating:</Text>
                  <HStack>
                    {Array(5)
                      .fill('')
                      .map((_, i) => (
                        <StarIcon
                          key={i}
                          color={i < Math.floor(product.rating) ? 'brand.500' : 'gray.300'}
                          size={14}
                        />
                      ))
                    }
                    <Text ml={1}>({product.rating} / 5)</Text>
                  </HStack>
                </HStack>
                <HStack>
                  <Text fontWeight="bold" w="200px">Stock:</Text>
                  <Text>{product.stock > 0 ? `${product.stock} units` : 'Out of stock'}</Text>
                </HStack>
                <HStack>
                  <Text fontWeight="bold" w="200px">Warranty:</Text>
                  <Text>1 Year</Text>
                </HStack>
              </Stack>
            </TabPanel>
            <TabPanel>
              <Stack spacing={4}>
                {[...Array(3)].map((_, i) => (
                  <Box key={i} p={4} borderWidth="1px" borderRadius="md" bg="gray.50">
                    <HStack mb={2} justify="space-between">
                      <HStack>
                        <HStack>
                          {Array(5)
                            .fill('')
                            .map((_, j) => (
                              <StarIcon
                                key={j}
                                color={j < 4 ? 'brand.500' : 'gray.300'}
                                size={16}
                              />
                            ))
                          }
                        </HStack>
                        <Text fontWeight="bold">Reviewer {i + 1}</Text>
                      </HStack>
                      <Text fontSize="sm" color="gray.500">1 week ago</Text>
                    </HStack>
                    <Text>Great product! I'm very satisfied with my purchase. The quality is excellent and it's exactly as described.</Text>
                  </Box>
                ))}
              </Stack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Box>
    </Container>
  );
};

export default ProductDetailPage;
