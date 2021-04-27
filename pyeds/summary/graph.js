// Created by Martin Strohalm

// get current url
var url = document.location.protocol +"//"+ document.location.hostname + document.location.pathname

// init size
var graphElm = d3.select("#graph");
var graphPadding = 15;
var graphWidth = graphElm.node().clientWidth;
var graphHeight = graphElm.node().clientHeight;
var graphSize = Math.min(graphWidth, graphHeight) - 2*graphPadding;

// get data limits
var nodesMaxCount = d3.max(nodesData, d => d.count);
var linksMaxCount = d3.max(linksData, d => d.count);

// init scales
var nodeRadiusScale = d3.scaleSqrt()
    .domain([0, nodesMaxCount])
    .range([5, 10])
    .clamp(true);

var linkColorScale = d3.scaleLinear()
    .domain([0, .5*linksMaxCount, linksMaxCount])
    .interpolate(d3.interpolateHcl)
    .range(["grey", "orange", "red"])
    .clamp(true);

// init graph containers
var graphSVG = d3.select("#graph")
    .append("svg")
    .attr("width", graphWidth)
    .attr("height", graphHeight);

var graph = graphSVG.append("g")
    .attr("class", "network");

var links = graph.append("g")
    .attr("class", "links");

var nodes = graph.append("g")
    .attr("class", "nodes");

// init controls
var enableHidden = createCheckboxItem(15, 15, "Hidden", true, updateGraphData);
var enableEnums = createCheckboxItem(15, 35, "Enums", true, updateGraphData);
var enableDDMaps = createCheckboxItem(15, 55, "DD Maps", true, updateGraphData);

// init simulation
var simulation = createSimulation();

// init tooltip
var tooltip = d3.select("#graph")
    .append("p")
    .attr("class", "tooltip")
    .style("opacity", 0);

// init drag events
var dragHandler = d3.drag()
    .on("start", onDragStarted)
    .on("drag", onDragDragged)
    .on("end", onDragEnded);

// create graph data
createNodes(nodesData);
createLinks(linksData);
updateGraphData();

// items creation

function updateGraphData() {

    // get all data
    var linkItems = Array.from(linksData);
    var nodeItems = Array.from(nodesData);

    // disable invisible
    if (enableHidden.value() == false) {
        nodeItems = nodeItems.filter(d => d.visible != 0);
    }

    // disable enums
    if (enableEnums.value() == false) {
        nodeItems = nodeItems.filter(d => d.type != 'n_enum');
    }

    // disable distribution maps
    if (enableDDMaps.value() == false) {
        nodeItems = nodeItems.filter(d => d.type != 'n_ddmap');
    }

    // get visible nodes map
    var visibleNodes = nodeItems.map(function (d) { return d.id });

    // hide disabled nodes
    nodes.selectAll("g.node").classed("disabled", d => visibleNodes.indexOf(d.id) == -1);

    // get valid links
    var linkItems = linkItems.filter(d => visibleNodes.indexOf(d.source_id) != -1 && visibleNodes.indexOf(d.target_id) != -1);

    // create links
    createLinks(linkItems);

    // update simulation
    simulation.nodes(nodeItems);
    simulation.force("link").links(linkItems);
    simulation.alpha(1).restart();
}

function createSimulation() {
    
    // init simulation
    var simulation = d3.forceSimulation()
        .force('charge', d3.forceManyBody()
            .distanceMax(.5*graphSize)
            .strength(d => d.layer != -1 ? -120*d.layer : -50))
        .force('center', d3.forceCenter(.5*graphWidth, .5*graphHeight))
        .force('x', d3.forceX(.5*graphWidth).strength(0.02))
        .force('y', d3.forceY(.5*graphHeight).strength(0.02))
        .force("link", d3.forceLink()
            .id(d => d.id)
            .distance(d => d.type == "l_dtype" ? 30 : 15))
        .force('collision', d3.forceCollide().radius(d => 2+nodeRadiusScale(d.count)));
    
    // set layout
    simulation.on("tick", function() {
        
        nodes.selectAll("circle")
            .attr("cx", function(d) { return d.x = Math.max(graphPadding, Math.min(graphWidth - graphPadding, d.x)); })
            .attr("cy", function(d) { return d.y = Math.max(graphPadding, Math.min(graphHeight - graphPadding, d.y)); });
        
        links.selectAll("line")
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);
    });
    
    return simulation;
}

function createNodes(items) {
    
    // reset positions
    var cx = .5*graphWidth;
    var cy = .5*graphHeight;
    var rand = d3.randomUniform(10, 100);
    
    items.forEach(function(d) {
            d.x = cx + rand();
            d.y = cy + rand();
        });
    
    // remove current
    nodes.selectAll(".node").remove();
    
    // create nodes
    var item = nodes.selectAll("g.node")
        .data(items)
        .enter().append("g")
        .attr("id", d => d.type + "_" + d.name.replace(/ /g, "_"))
        .attr("class", d => "node " + d.type)
        .classed("hidden", d => d.visible == 0);
    
    var circle = item.append("circle")
        .attr("r", d => nodeRadiusScale(d.count));
    
    // enable tooltip
    item.on("mouseover", function(d) { showNodeInfo(this, d, true); });
    item.on("mouseout", function(d) { showNodeInfo(this, d, false); });
    
    // enable jumps
    item.on("click", onNodeClick);
    
    // enable node dragging
    dragHandler(item);
}

function createLinks(items) {
    
    // remove current
    links.selectAll(".link").remove();
    
    // create links
    var item = links.selectAll("g.link")
        .data(items)
        .enter().append("g")
        .attr("class", "link");
    
    item.append("line")
        .attr("class", "conn")
        .attr("stroke-width", 1.5)
        .attr("stroke", d => linkColorScale(d.count));
    
    item.append("line")
        .attr("class", "spacer")
        .attr("stroke-width", 10)
        .attr("stroke", "transparent");
    
    // enable tooltip
    item.on("mouseover", function(d) { showLinkInfo(this, d, true); });
    item.on("mouseout", function(d) { showLinkInfo(this, d, false); });
}

function createCheckboxItem(x, y, text, value, callback) {

    var size = 12;

    var item = graph.append("g")
        .attr("class", "checkbox")
        .classed("checked", value);

    var svg = item.append("svg")
        .attr("width", size)
        .attr("height", size);

    var check = item.append("rect")
        .attr("class", "handle")
        .attr("x", x-0.5*size)
        .attr("y", y-0.5*size)
        .attr("width", size - 2)
        .attr("height", size - 2)
        .attr("rx", 3)
        .attr("ry", 3)
        .attr("pointer-events", "fill");

    var label = item.append("text")
        .attr("class", "label")
        .attr("x", x + size)
        .attr("y", y)
        .attr("alignment-baseline", "middle")
        .text(text);

    var onClick = function () {
        item.value(!item.classed("checked"));
        callback();
    };

    check.on("click", onClick);
    label.on("click", onClick);

    item.value = function (val) {

        if (typeof val == 'undefined') {
            return item.classed("checked");
        }
        else {
            item.classed("checked", val);
        }
    };

    return item;
}

// tooltip display

function showTooltip(text) {
    
    if (text != "") {
        tooltip
            .html(text)
            .style("left", (d3.event.pageX + 15) + "px")
            .style("top", (d3.event.pageY + 15) + "px")
            .transition()
            .duration(200)
            .style("opacity", .85)
            .transition()
            .delay(5000)
            .duration(500)
            .style("opacity", 0);
    }
    else {
        tooltip
            .transition()
            .duration(500)
            .style("opacity", 0);
    }
}

function showNodeInfo(n, d, show) {
    
    if (!show) {
        showTooltip("");
        nodes.selectAll(".node").classed("highlight", false);
        links.selectAll(".link").classed("highlight", false);
        return;
    }
    
    var html = d.count != -1
            ? d.name + "<br /><em>" + d.display + " (" + d.count + ")</em>"
            : d.name;
    
    showTooltip(html);
    
    var selectedLinks = links.selectAll(".link")
        .filter(o => o.source === d || o.target === d)
        .classed("highlight", true);;
    
    var selectedNodes = selectedLinks.data().map(o => o.target)
        .concat(selectedLinks.data().map(o => o.source));
    
    nodes.selectAll(".node")
        .filter(o => o === d || selectedNodes.indexOf(o) != -1)
        .classed("highlight", true);
}

function showLinkInfo(n, d, show) {
    
    if (!show) {
        showTooltip("");
        d3.select(n).classed("highlight", false);
        nodes.selectAll(".node").classed("highlight", false);
        d.source.ms2cov = null;
        d.target.ms2cov = null;
        return;
    }
    
    var name = d.source.name + "<br />" + d.target.name;
    var html = d.count != -1
            ? name + "<br />(" + d.count + ")"
            : name;
    
    showTooltip(html);
    
    d3.select(n).classed("highlight", true);
    
    nodes.selectAll(".node")
        .filter(o => o === d.source || o === d.target)
        .classed("highlight", true);
}

function highlightNode(id, enable) {
    
    // select node
    var item = graph.select(id+" circle");
    
    // pop node
    if (enable) {
        item.classed("pop", true)
            .transition().duration(500)
                .attr("r", d => nodeRadiusScale(d.count) + 10)
            .transition().duration(500)
                .attr("r", d => nodeRadiusScale(d.count));
    }
    
    // remove highlight
    else {
        item.classed("pop", false)
            .transition().duration(100)
                .attr("r", d => nodeRadiusScale(d.count));
    }
}

// core events

function onDragStarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function onDragDragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function onDragEnded(d) {
    
    if (!d3.event.active) simulation.alphaTarget(0);
  
    if (d3.event.sourceEvent.altKey || d3.event.sourceEvent.ctrlKey) {
        d3.select(this).classed("fixed", d.fixed = true);
    }
    else {
        d.fx = null;
        d.fy = null;
    }
}

function onNodeClick(d) {
    
    if (d3.event.altKey || d3.event.ctrlKey) {
        d3.select(this).classed("fixed", d.fixed = false);
        d.fx = null;
        d.fy = null;
    }
    else if (d.anchor != '') {
        window.location.href = url + "#" + d.anchor;
    }
}
