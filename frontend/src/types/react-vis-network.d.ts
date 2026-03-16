declare module 'react-vis-network' {
  import { RefObject } from 'react';

  interface NetworkProps {
    ref?: RefObject<any>;
    data?: {
      nodes: any[];
      edges: any[];
    };
    options?: any;
    onClick?: (params: any) => void;
    style?: React.CSSProperties;
  }

  interface NetworkRef {
    zoomIn: (options?: { scale?: number }) => void;
    zoomOut: (options?: { scale?: number }) => void;
    fit: (options?: { animation?: boolean }) => void;
  }

  export const Network: React.FC<NetworkProps>;
}
