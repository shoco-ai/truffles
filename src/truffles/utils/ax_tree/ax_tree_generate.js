function generateAccessibilityTree(truffles_attr_id) {
    let counter = 0;

    const NodeType = {
        ELEMENT_NODE: 1,
        ATTRIBUTE_NODE: 2,
        TEXT_NODE: 3,
        CDATA_SECTION_NODE: 4,
        ENTITY_REFERENCE_NODE: 5,  // Legacy, deprecated
        ENTITY_NODE: 6,           // Legacy, deprecated
        PROCESSING_INSTRUCTION_NODE: 7,
        COMMENT_NODE: 8,
        DOCUMENT_NODE: 9,
        DOCUMENT_TYPE_NODE: 10,
        DOCUMENT_FRAGMENT_NODE: 11,
        NOTATION_NODE: 12         // Legacy, deprecated
    };

    function getUniqueId() {
        return `${counter++}`;
    }

    function getNodeName(node) {
        if (node.nodeType === 3) return '#text';
        return node.tagName ? node.tagName.toLowerCase() : node.nodeName.toLowerCase();
    }

    function getNodeRole(node) {
        // Skip role check for text nodes
        if (node.nodeType === 3) return null;

        // Get explicit role
        const explicitRole = node.getAttribute ? node.getAttribute('role') : null;
        if (explicitRole) return explicitRole;

        // Default roles for common elements
        const tagName = node.tagName ? node.tagName.toLowerCase() : '';
        const roleMap = {
            'a': 'link',
            'button': 'button',
            'h1': 'heading',
            'h2': 'heading',
            'h3': 'heading',
            'h4': 'heading',
            'h5': 'heading',
            'h6': 'heading',
            'img': 'img',
            'input': 'textbox',
            'ul': 'list',
            'ol': 'list',
            'li': 'listitem'
        };
        return roleMap[tagName] || 'generic';
    }

    function getNodeProperties(node) {
        const properties = {};

        // Handle text nodes
        if (node.nodeType === NodeType.TEXT_NODE) {
            const text = node.textContent.trim();
            if (text) {
                properties.text = text;
            }
            return properties;
        }

        // Handle element nodes
        if (node.nodeType === NodeType.ELEMENT_NODE) {
            // Get attributes
            if (node.attributes) {
                for (let i = 0; i < node.attributes.length; i++) {
                    properties[node.attributes[i].name] = node.attributes[i].value;
                }
            }

            // Get computed styles
            try {
                const style = window.getComputedStyle(node);
                properties.isVisible = style.display !== 'none' &&
                    style.visibility !== 'hidden' &&
                    style.opacity !== '0';
            } catch (e) {
                properties.isVisible = true; // Default to visible if we can't determine
            }


            // TODO: get bounding box info
            try {
                const style = window.getComputedStyle(node);
                properties.isVisible = style.display !== 'none' &&
                    style.visibility !== 'hidden' &&
                    style.opacity !== '0';
                // Get bounding box information
                const rect = node.getBoundingClientRect();
                properties.boundingBox = {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    right: rect.right,
                    bottom: rect.bottom,
                    left: rect.left
                };
            } catch (e) {
                properties.isVisible = true; // Default to visible if we can't determine
            }

            // Get text content
            const text = node.textContent ? node.textContent.trim() : '';
            // const text = getFilteredTextContent(node);
            if (text) {
                properties.text = text;
            }
        }

        return properties;
    }

    function getFilteredTextContent(node) {
        if (!node) return '';

        // Skip script and style tags
        if (node.nodeType === NodeType.ELEMENT_NODE &&
            node.tagName &&
            ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(node.tagName.toUpperCase())) {
            return '';
        }

        // Handle text nodes
        if (node.nodeType === NodeType.TEXT_NODE) {
            return node.textContent.trim();
        }

        // Recursively process child nodes
        let text = '';
        if (node.childNodes && node.childNodes.length > 0) {
            for (let i = 0; i < node.childNodes.length; i++) {
                text += getFilteredTextContent(node.childNodes[i]) + ' ';
            }
        }

        return text.trim();
    }

    function processNode(node) {
        if (!node) return null;

        // Skip script and style tags
        if (node.nodeType === NodeType.ELEMENT_NODE &&
            node.tagName &&
            ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(node.tagName.toUpperCase())) {
            return null;
        }

        // Create node object
        const nodeObj = {
            id: getUniqueId(),
            name: getNodeName(node),
            role: getNodeRole(node),
            properties: getNodeProperties(node),
            children: []
        };

        // Mark the actual DOM node with the ID (only for element nodes)
        if (node.nodeType === NodeType.ELEMENT_NODE) {
            try {
                node.setAttribute(truffles_attr_id, nodeObj.id);
            } catch (e) {
                // Ignore if we can't set the attribute
                console.log("Error setting accessibility attribute", e);
            }
        }

        // Process children
        if (node.childNodes && node.childNodes.length > 0) {
            for (let i = 0; i < node.childNodes.length; i++) {
                const childResult = processNode(node.childNodes[i]);
                if (childResult) {
                    nodeObj.children.push(childResult);
                }
            }
        }

        return nodeObj;
    }

    // Start processing from document.body
    const result = processNode(document.body);
    return result;
}
