#  Created by Martin Strohalm, Thermo Fisher Scientific

# import modules
import xml.etree.cElementTree as etree
from datetime import datetime
from .lockable import Lockable

# define constants
POSIX_EPOCH_AS_DOTNET = 621355968000000000


class Workflow(Lockable):
    """
    The pyeds.Workflow class is used to hold all the meta-data of a workflow.
    
    Attributes:
        
        ID: int
            Workflow ID.
        
        GUID: str
            Workflow GUID.
        
        Name: str
            Workflow name.
        
        Description: str
            Basic descriptions.
        
        Type: str
            Workflow type.
        
        Level: int
            Workflow level.
        
        Version: int
            Used workflow version.
        
        Date: datetime
            Start date.
        
        State: int
            Execution state.
        
        Study: str
            Associated study name.
        
        User: str
            User name.
        
        Software: str
            Software name.
        
        Machine: str
            Machine name.
        
        XML: str
            Full workflow XML.
        
        Nodes: (pyeds.WorkflowNode,)
            Workflow processing node.
        
        Messages: (pyeds.WorkflowMessage,)
            Workflow processing messages.
    """
    
    
    def __init__(self):
        """Initializes a new instance of Workflow."""
        
        super().__init__()
        
        self.ID = None
        self.GUID = None
        self.Name = None
        self.Description = None
        self.Type = None
        self.Level = None
        self.Version = None
        
        self.Date = None
        self.State = None
        
        self.Study = None
        self.User = None
        self.Software = None
        self.Machine = None
        
        self._nodes = {}
        self._messages = []
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return "%s (%s, %s)" % (self.Name, self.ID, self.Type)
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def Nodes(self):
        """
        Gets workflow processing messages.
        
        Returns:
            (pyeds.WorkflowNode,)
                All workflow nodes.
        """
        
        return tuple(self._nodes.values())
    
    
    @property
    def Messages(self):
        """
        Gets workflow processing messages.
        
        Returns:
            (pyeds.WorkflowMessage,)
                All workflow messages.
        """
        
        return tuple(self._messages)
    
    
    def GetNode(self, node_id):
        """
        Gets the processing node by its ID.
        
        Args:
            node_id: int
                Node ID.
        
        Returns:
            pyeds.WorkflowNode
                Processing node.
        """
        
        return self._nodes[node_id]
    
    
    def AddNode(self, node):
        """
        Adds given workflow node.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            node: pyeds.WorkflowNode
                Workflow node to be added.
        """
        
        self._nodes[node.ID] = node
    
    
    def AddMessage(self, message):
        """
        Adds given workflow message.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            message: pyeds.WorkflowMessage
                Workflow message to be added.
        """
        
        self._messages.append(message)
    
    
    @staticmethod
    def FromDBData(data):
        """
        Creates instance from database data.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            data: dict
                Database data.
        
        Returns:
            pyeds.Workflow
                Workflow instance.
        """
        
        # init workflow
        workflow = Workflow()
        
        workflow.ID = data['WorkflowID']
        workflow.GUID = data['WorkflowGUID']
        workflow.Name = data['WorkflowName']
        workflow.Description = data['WorkflowDescription']
        workflow.Type = data['WorkflowType']
        workflow.Level = data['Level']
        workflow.Version = data['Version']
        workflow.Date = data['WorkflowStartDate']
        workflow.State = data['WorkflowState']
        workflow.Study = data['Study']
        workflow.User = data['User']
        workflow.Software = data['SoftwareVersion']
        workflow.Machine = data['MachineName']
        workflow.XML = data['WorkflowXML']
        
        # convert time
        if workflow.Date:
            workflow.Date = datetime.strptime(workflow.Date[:19], "%Y-%m-%d %H:%M:%S")
        
        # retrieve nodes
        tree = etree.fromstring(workflow.XML)
        for node_elm in tree.iter('WorkflowNode'):
            node = WorkflowNode.FromDBData(node_elm)
            if node is not None:
                workflow.AddNode(node)
        
        return workflow


class WorkflowMessage(Lockable):
    """
    The pyeds.WorkflowMessage class is used to hold all the meta-data of a
    workflow message.
    
    Attributes:
        
        ID: int
            Message ID.
        
        WorkflowID: str
            Workflow ID.
        
        Level: int
            Message level.
        
        NodeName: str
            Processing node name.
        
        Time: datetime
            Time stamp.
        
        Kind: int
            Message kind.
        
        Message: str
            Message text.
    """
    
    
    def __init__(self):
        """Initializes a new instance of WorkflowMessage."""
        
        super().__init__()
        
        self.ID = None
        self.WorkflowID = None
        self.Level = None
        self.NodeName = None
        self.Time = None
        self.Kind = None
        self.Message = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return self.Message
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @staticmethod
    def FromDBData(data):
        """
        Creates instance from database data.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            data: dict
                Database data.
        
        Returns:
            pyeds.WorkflowMessage
                Workflow message instance.
        """
        
        # init message
        message = WorkflowMessage()
        
        message.ID = data['MessageID']
        message.WorkflowID = data['WorkflowID']
        message.Level = data['Level']
        message.NodeName = data['ProcessingNodeName']
        message.Time = data['Time']
        message.Kind = data['MessageKind']
        message.Message = data['Message']
        
        # convert time
        if message.Time is not None:
            time_stamp = (message.Time - POSIX_EPOCH_AS_DOTNET) // 1e7
            message.Time = datetime.fromtimestamp(time_stamp)
        
        return message


class WorkflowNode(Lockable):
    """
    The pyeds.WorkflowNode class is used to hold all the meta-data of a workflow
    processing node.
    
    Attributes:
        
        ID: int
            Node ID.
        
        GUID: str
            Unique node GUID.
        
        Name: str
            Node name.
        
        DisplayName: str
            Node display name.
        
        Description: str
            Node description.
        
        Category: str
            Category name.
        
        Publisher: str
            Publisher name.
        
        MainVersion: str
            Main version number.
        
        MinorVersion: str
            Main version number.
        
        ParentNodes: (int,)
            Parent nodes IDs.
        
        State: str
            Node state.
        
        Parameters: (pyeds.WorkflowNodeParam,)
            Node parameters.
    """
    
    
    def __init__(self):
        """Initializes a new instance of WorkflowNode."""
        
        super().__init__()
        
        self.ID = None
        self.GUID = None
        self.Name = None
        self.DisplayName = None
        self.Description = None
        self.Category = None
        self.Publisher = None
        self.MainVersion = None
        self.MinorVersion = None
        self.ParentNodes = None
        self.State = None
        
        self._params = []
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return "%s (%s)" % (self.DisplayName, self.ID)
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @property
    def Parameters(self):
        """
        Gets node parameters.
        
        Returns:
            (pyeds.WorkflowNodeParam,)
                All node parameters.
        """
        
        return tuple(self._params)
    
    
    def AddParam(self, param):
        """
        Adds given node parameter.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            param: pyeds.WorkflowMessage
                Node parameter to be added.
        """
        
        self._params.append(param)
    
    
    @staticmethod
    def FromDBData(data):
        """
        Creates instance from database data.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            data: Element
                WorkflowNode element.
        
        Returns:
            pyeds.WorkflowNode
                Workflow node instance.
        """
        
        # init node
        node = WorkflowNode()
        
        node.ID = int(data.get('ProcessingNodeNumber', -1))
        node.GUID = data.get('Guid', None)
        node.Name = data.get('ProcessingNodeName', None)
        node.DisplayName = data.get('FriendlyName', None)
        node.Description = data.get('Description', None)
        node.Category = data.get('Category', None)
        node.Publisher = data.get('Publisher', None)
        node.MainVersion = data.get('MainVersion', None)
        node.MinorVersion = data.get('MinorVersion', None)
        node.ParentNodes = data.get('ParentProcessingNodeNumber', None)
        node.State = data.get('NodeState', None)
        
        # parse parent nodes
        if node.ParentNodes is not None:
            node.ParentNodes = tuple(int(x) for x in node.ParentNodes.split(";"))
        
        # retrieve parameters
        for param_elm in data.iter('ProcessingNodeParameter'):
            param = WorkflowNodeParam.FromDBData(param_elm)
            if param is not None:
                node.AddParam(param)
        
        return node


class WorkflowNodeParam(Lockable):
    """
    The pyeds.WorkflowNodeParam class is used to hold all the meta-data of a
    workflow processing node parameter.
    
    Attributes:
        
        Name: str
            Parameter name.
        
        DisplayName: str
            Parameter display name.
        
        Category: str
            Category name.
        
        Purpose: str
            Parameter purpose.
        
        Value: str
            Set value.
        
        DisplayValue: str
            Set value readable version.
    """
    
    
    def __init__(self):
        """Initializes a new instance of WorkflowNodeParam."""
        
        super().__init__()
        
        self.Name = None
        self.DisplayName = None
        self.Category = None
        self.Purpose = None
        self.Value = None
        self.DisplayValue = None
    
    
    def __str__(self):
        """Gets standard string representation."""
        
        return "%s [%s]" % (self.DisplayName, self.DisplayValue)
    
    
    def __repr__(self):
        """Gets debug string representation."""
        
        return "%s(%s)" % (self.__class__.__name__, self.__str__())
    
    
    @staticmethod
    def FromDBData(data):
        """
        Creates instance from database data.
        
        This method is not intended to be used by user. It is used automatically
        by the library itself.
        
        Args:
            data: Element
                ProcessingNodeParameter element.
        
        Returns:
            pyeds.WorkflowNodeParam
                Node parameter.
        """
        
        param = WorkflowNodeParam()
        
        param.Name = data.get('Name', None)
        param.DisplayName = data.get('FriendlyName', None)
        param.Category = data.get('Category', None)
        param.Purpose = data.get('IntendedPurpose', None)
        param.Value = data.text
        param.DisplayValue = data.get('DisplayValue', None)
        
        return param
