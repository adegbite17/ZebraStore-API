
import { useState } from 'react';
import logo from "../../assets/zebra.jpg"
import { 
  Box, 
  Flex, 
  Text, 
  IconButton, 
  Button, 
  Stack, 
  Collapse, 
  Icon, 
  Link,
  Image, 
  Popover, 
  PopoverTrigger, 
  PopoverContent, 
  useColorModeValue, 
  useBreakpointValue, 
  useDisclosure,
  Input,
  InputGroup,
  InputRightElement,
  Badge,
  HStack,
  Avatar
} from '@chakra-ui/react';
import { 
  Menu as HamburgerIcon, 
  X as CloseIcon, 
  ChevronDown as ChevronDownIcon, 
  ChevronRight as ChevronRightIcon, 
  Search as SearchIcon,
  ShoppingCart as ShoppingCartIcon,
  User as UserIcon
} from 'lucide-react';
import { Link as RouterLink } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';

const Header = () => {
  const { isOpen, onToggle } = useDisclosure();
  const { totalItems } = useCart();
  const { user, isAuthenticated, logout } = useAuth();
  const [searchValue, setSearchValue] = useState('');

  return (
    <Box>
      <Flex
        bg={useColorModeValue('white', 'gray.800')}
        color={useColorModeValue('gray.600', 'white')}
        minH={'60px'}
        py={{ base: 2 }}
        px={{ base: 4 }}
        borderBottom={1}
        borderStyle={'solid'}
        borderColor={useColorModeValue('gray.200', 'gray.900')}
        align={'center'}
        position="sticky"
        top="0"
        zIndex="1000"
        boxShadow="sm"
      >
        <Flex
          flex={{ base: 1, md: 'auto' }}
          ml={{ base: -2 }}
          display={{ base: 'flex', md: 'none' }}
        >
          <IconButton
            onClick={onToggle}
            icon={
              isOpen ? <CloseIcon size={24} /> : <HamburgerIcon size={24} />
            }
            variant={'ghost'}
            aria-label={'Toggle Navigation'}
          />
        </Flex>
        <Flex flex={{ base: 1 }} justify={{ base: 'center', md: 'start' }} alignItems="center">
       

          <Image src={logo} w="50px" h="50px"/>

          <Flex display={{ base: 'none', md: 'flex' }} ml={10}>
            <DesktopNav />
          </Flex>
        </Flex>

        <Stack
          flex={{ base: 1, md: 2 }}
          justify={'flex-end'}
          direction={'row'}
          spacing={4}
          align="center"
        >
          <InputGroup w={{ base: '100%', md: '300px' }} size="sm" display={{ base: 'none', md: 'block' }}>
            <Input 
              placeholder="Search products..." 
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              borderRadius="full" 
              bg="gray.100"
            />
            <InputRightElement>
              <IconButton
                aria-label="Search"
                icon={<SearchIcon size={18} />}
                size="sm"
                variant="ghost"
                borderRadius="full"
              />
            </InputRightElement>
          </InputGroup>

          <Box position="relative" display="flex" alignItems="center">
            <IconButton
              as={RouterLink}
              to="/cart"
              aria-label="Shopping cart"
              icon={<ShoppingCartIcon size={20} />}
              variant="ghost"
            />
            {totalItems > 0 && (
              <Badge
                borderRadius="full"
                colorScheme="red"
                position="absolute"
                top="-5px"
                right="-5px"
                fontSize="0.8em"
              >
                {totalItems}
              </Badge>
            )}
          </Box>

          {isAuthenticated ? (
            <Popover trigger="hover" placement="bottom-end">
              <PopoverTrigger>
                <Button variant="ghost" p={0}>
                  <Avatar size="sm" name={user?.name} bg="brand.500" color="white" />
                </Button>
              </PopoverTrigger>
              <PopoverContent width="200px" p={4}>
                <Stack>
                  <Text fontWeight="medium">{user?.name}</Text>
                  <Text fontSize="sm" color="gray.500">{user?.email}</Text>
                  <Button as={RouterLink} to="/profile" size="sm" variant="ghost">
                    My Profile
                  </Button>
                  <Button as={RouterLink} to="/orders" size="sm" variant="ghost">
                    Orders
                  </Button>
                  <Button size="sm" variant="ghost" onClick={logout}>
                    Logout
                  </Button>
                </Stack>
              </PopoverContent>
            </Popover>
          ) : (
            <HStack spacing={2}>
              <Button as={RouterLink} to="/login" variant="ghost" size="sm">
                Sign In
              </Button>
              <Button
                as={RouterLink}
                to="/register"
                display={{ base: 'none', md: 'inline-flex' }}
                fontSize={'sm'}
                fontWeight={600}
                color={'white'}
                bg={'brand.500'}
                size="sm"
                _hover={{
                  bg: 'brand.600',
                }}
              >
                Sign Up
              </Button>
            </HStack>
          )}
        </Stack>
      </Flex>

      <Collapse in={isOpen} animateOpacity>
        <MobileNav />
      </Collapse>
    </Box>
  );
};

const DesktopNav = () => {
  const linkColor = useColorModeValue('gray.600', 'gray.200');
  const linkHoverColor = useColorModeValue('brand.500', 'white');
  const popoverContentBgColor = useColorModeValue('white', 'gray.800');

  return (
    <Stack direction={'row'} spacing={4}>
      {NAV_ITEMS.map((navItem) => (
        <Box key={navItem.label}>
          <Popover trigger={'hover'} placement={'bottom-start'}>
            <PopoverTrigger>
              <Link
                as={RouterLink}
                p={2}
                to={navItem.href ?? '#'}
                fontSize={'sm'}
                fontWeight={500}
                color={linkColor}
                _hover={{
                  textDecoration: 'none',
                  color: linkHoverColor,
                }}
              >
                {navItem.label}
                {navItem.children && (
                  <Icon
                    as={ChevronDownIcon}
                    w={5}
                    h={5}
                    ml={1}
                  />
                )}
              </Link>
            </PopoverTrigger>

            {navItem.children && (
              <PopoverContent
                border={0}
                boxShadow={'xl'}
                bg={popoverContentBgColor}
                p={4}
                rounded={'xl'}
                minW={'sm'}
              >
                <Stack>
                  {navItem.children.map((child) => (
                    <DesktopSubNav key={child.label} {...child} />
                  ))}
                </Stack>
              </PopoverContent>
            )}
          </Popover>
        </Box>
      ))}
    </Stack>
  );
};

const DesktopSubNav = ({ label, href, subLabel }: NavItem) => {
  return (
    <Link
      as={RouterLink}
      to={href ?? '#'}
      role={'group'}
      display={'block'}
      p={2}
      rounded={'md'}
      _hover={{ bg: useColorModeValue('brand.50', 'gray.900') }}
    >
      <Stack direction={'row'} align={'center'}>
        <Box>
          <Text
            transition={'all .3s ease'}
            _groupHover={{ color: 'brand.500' }}
            fontWeight={500}
          >
            {label}
          </Text>
          <Text fontSize={'sm'}>{subLabel}</Text>
        </Box>
        <Flex
          transition={'all .3s ease'}
          transform={'translateX(-10px)'}
          opacity={0}
          _groupHover={{ opacity: '100%', transform: 'translateX(0)' }}
          justify={'flex-end'}
          align={'center'}
          flex={1}
        >
          <Icon color={'brand.500'} w={5} h={5} as={ChevronRightIcon} />
        </Flex>
      </Stack>
    </Link>
  );
};

const MobileNav = () => {
  return (
    <Stack
      bg={useColorModeValue('white', 'gray.800')}
      p={4}
      display={{ md: 'none' }}
    >
      {NAV_ITEMS.map((navItem) => (
        <MobileNavItem key={navItem.label} {...navItem} />
      ))}
      <InputGroup size="sm" mt={2}>
        <Input 
          placeholder="Search products..." 
          borderRadius="full" 
          bg="gray.100"
        />
        <InputRightElement>
          <IconButton
            aria-label="Search"
            icon={<SearchIcon size={18} />}
            size="sm"
            variant="ghost"
            borderRadius="full"
          />
        </InputRightElement>
      </InputGroup>
    </Stack>
  );
};

const MobileNavItem = ({ label, children, href }: NavItem) => {
  const { isOpen, onToggle } = useDisclosure();

  return (
    <Stack spacing={4} onClick={children && onToggle}>
      <Flex
        py={2}
        as={RouterLink}
        to={href ?? '#'}
        justify={'space-between'}
        align={'center'}
        _hover={{
          textDecoration: 'none',
        }}
      >
        <Text
          fontWeight={600}
          color={useColorModeValue('gray.600', 'gray.200')}
        >
          {label}
        </Text>
        {children && (
          <Icon
            as={ChevronDownIcon}
            transition={'all .25s ease-in-out'}
            transform={isOpen ? 'rotate(180deg)' : ''}
            w={6}
            h={6}
          />
        )}
      </Flex>

      <Collapse in={isOpen} animateOpacity style={{ marginTop: '0!important' }}>
        <Stack
          mt={2}
          pl={4}
          borderLeft={1}
          borderStyle={'solid'}
          borderColor={useColorModeValue('gray.200', 'gray.700')}
          align={'start'}
        >
          {children &&
            children.map((child) => (
              <Link
                key={child.label}
                py={2}
                as={RouterLink}
                to={child.href ?? '#'}
              >
                {child.label}
              </Link>
            ))}
        </Stack>
      </Collapse>
    </Stack>
  );
};

interface NavItem {
  label: string;
  subLabel?: string;
  children?: Array<NavItem>;
  href?: string;
}

const NAV_ITEMS: Array<NavItem> = [
  {
    label: 'Home',
    href: '/',
  },
  {
    label: 'Shop',
    href: '/products',
    children: [
      {
        label: 'Electronics',
        subLabel: 'Laptops, Phones, and more',
        href: '/products?category=Electronics',
      },
      {
        label: 'Clothing',
        subLabel: 'Men\'s and Women\'s Fashion',
        href: '/products?category=Fashion',
      },
      {
        label: 'Home & Kitchen',
        subLabel: 'Appliances and Decor',
        href: '/products?category=Home & Kitchen',
      },
    ],
  },
  {
    label: 'New Arrivals',
    href: '/products?new=true',
  },
  {
    label: 'Sale',
    href: '/products?sale=true',
  },
];

export default Header;
