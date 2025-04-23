import streamlit as st
from pyvis.network import Network
import json
import os
import tempfile

st.set_page_config(layout="wide")

st.title("🌌 Pat Bajari's Academic Constellation")
st.markdown("A Tribute to His Scholarly Legacy (1969–2025)")

# Load data
data_path = os.path.join("public", "full_data.json")
with open(data_path, "r") as f:
    data = json.load(f)

nodes = data["nodes"]
links = data["links"]

# Create Pyvis network
net = Network(height="800px", width="100%", bgcolor="#0a0a2a", font_color="white")
net.barnes_hut()

# Add nodes
for node in nodes:
    color = "#f9c74f" if node["type"] == "central" else "#90be6d" if node["type"] == "coauthor" else "#f8961e"
    title = f"{node['label']}"
    if node["type"] == "paper":
        title += f"\n📅 {node['year']}"

    net.add_node(
        node["id"],
        label=node["label"],
        size=node["size"] * 2,
        title=title,
        color=color,
        font={"size": 20, "color": "white", "strokeWidth": 1, "strokeColor": "#000000"},
        shadow=True,
        shape="star" if node["type"] == "central" else "dot"
    )

# Add links
for link in links:
    net.add_edge(link["source"], link["target"], value=link["value"], color="#aaaaaa")

# Custom options with starfield background effect
net.set_options("""
{
  "nodes": {
    "shape": "dot",
    "shadow": true
  },
  "edges": {
    "color": {
      "color": "#aaaaaa"
    },
    "smooth": {
      "type": "dynamic"
    }
  },
  "physics": {
    "forceAtlas2Based": {
      "gravitationalConstant": -50,
      "centralGravity": 0.005,
      "springLength": 120,
      "springConstant": 0.08
    },
    "minVelocity": 0.75,
    "solver": "forceAtlas2Based"
  },
  "interaction": {
    "hover": true,
    "tooltipDelay": 100
  }
}
""")

# Export to HTML
with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".html") as tmp_file:
    net.save_graph(tmp_file.name)
    
    # Read the saved graph
    html_content = open(tmp_file.name, "r", encoding="utf-8").read()
    
    # Insert starry night background CSS and JS
    starry_background = """
    <style>
    #mynetwork {
        margin: 0;
        padding: 0;
        background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
        position: relative;
        overflow: hidden;
    }
    
    .star {
        position: absolute;
        background-color: white;
        border-radius: 50%;
        animation: twinkle 5s infinite;
        z-index: 0;
        pointer-events: none;
    }
    
    @keyframes twinkle {
        0% {opacity: 0.3;}
        50% {opacity: 1;}
        100% {opacity: 0.3;}
    }
    
    /* Ensure nodes and edges appear above stars */
    canvas {
        z-index: 1;
        position: relative;
    }
    </style>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Delay to ensure network is fully loaded
        setTimeout(function() {
            const networkDiv = document.getElementById('mynetwork');
            if (networkDiv) {
                const width = networkDiv.offsetWidth;
                const height = networkDiv.offsetHeight;
                
                // Create stars
                for (let i = 0; i < 300; i++) {
                    const star = document.createElement('div');
                    star.className = 'star';
                    
                    // Random position
                    const left = Math.random() * width;
                    const top = Math.random() * height;
                    
                    // Random size (0.5px to 3px)
                    const size = 0.5 + Math.random() * 2.5;
                    
                    // Random animation delay
                    const delay = Math.random() * 5;
                    
                    // Apply styles
                    star.style.left = left + 'px';
                    star.style.top = top + 'px';
                    star.style.width = size + 'px';
                    star.style.height = size + 'px';
                    star.style.animationDelay = delay + 's';
                    star.style.opacity = Math.random() * 0.7 + 0.3;
                    
                    networkDiv.appendChild(star);
                }
            }
        }, 1000); // Wait 1 second for network to initialize
    });
    </script>
    <script>
document.addEventListener("DOMContentLoaded", function () {
    setTimeout(function () {
        if (window.network) {
            const allNodes = network.body.data.nodes.get();
            const updateDimmed = () => {
                network.body.data.nodes.update(allNodes.map(n => ({
                    id: n.id,
                    color: { ...n.color, opacity: 0.2 },
                    font: { color: '#666' }
                })));
            };

            const resetNodes = () => {
                network.body.data.nodes.update(allNodes.map(n => ({
                    id: n.id,
                    color: { ...n.color, opacity: 1 },
                    font: { color: 'white' }
                })));
            };

            network.on("click", function (params) {
                if (params.edges.length > 0) {
                    const edgeId = params.edges[0];
                    const edge = network.body.data.edges.get(edgeId);
                    const connectedNodeIds = [edge.from, edge.to];

                    updateDimmed();

                    // Highlight only connected nodes
                    network.body.data.nodes.update(connectedNodeIds.map(id => ({
                        id: id,
                        color: { ...network.body.data.nodes.get(id).color, opacity: 1 },
                        font: { color: 'white' }
                    })));
                } else {
                    resetNodes();
                }
            });
        }
    }, 1000);
});
</script>

    """
    
    
    # Insert the starry background HTML before the closing body tag
    html_content = html_content.replace('</body>', starry_background + '</body>')
    
    # Write the modified HTML back to the file
    with open(tmp_file.name, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    tmp_file_path = tmp_file.name

# Render in Streamlit
st.components.v1.html(open(tmp_file_path, "r", encoding="utf-8").read(), height=850)

# Sidebar Legend
with st.sidebar:
    st.subheader("Legend")
    st.markdown("<span style='color:#f9c74f'>●</span> Pat Bajari", unsafe_allow_html=True)
    st.markdown("<span style='color:#90be6d'>●</span> Co-authors", unsafe_allow_html=True)
    st.markdown("<span style='color:#f8961e'>●</span> Publications", unsafe_allow_html=True)
    st.markdown("\nData source: `public/data.json`")