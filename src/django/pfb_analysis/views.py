from datetime import datetime

import us

from django.utils.text import slugify

from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.filters import DjangoFilterBackend, OrderingFilter
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from pfb_analysis.models import AnalysisJob, Neighborhood
from pfb_analysis.serializers import AnalysisJobSerializer, NeighborhoodSerializer
from pfb_network_connectivity.pagination import OptionalLimitOffsetPagination
from pfb_network_connectivity.filters import (OrgAutoFilterBackend,
                                              SelfUserAutoFilterBackend,
                                              AnalysisJobStatusFilterSet)
from pfb_network_connectivity.permissions import IsAdminOrgAndAdminCreateEditOnly, RestrictedCreate


class AnalysisJobViewSet(ModelViewSet):
    """For listing or retrieving analysis jobs."""

    queryset = AnalysisJob.objects.all()
    serializer_class = AnalysisJobSerializer
    permission_classes = (RestrictedCreate,)
    filter_class = AnalysisJobStatusFilterSet
    filter_backends = (DjangoFilterBackend, OrderingFilter, OrgAutoFilterBackend)
    ordering_fields = ('created_at', 'modified_at')
    ordering = ('-created_at',)

    def perform_create(self, serializer):
        """ Start analysis jobs as soon as created """
        instance = serializer.save()
        instance.run()

    @detail_route(methods=['post'])
    def cancel(self, request, pk=None):
        job = self.get_object()
        job.cancel(reason='AnalysisJob terminated via API by {} at {}'
                          .format(request.user.email, datetime.utcnow()))
        serializer = AnalysisJobSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NeighborhoodViewSet(ModelViewSet):
    """For listing or retrieving neighborhoods."""

    queryset = Neighborhood.objects.all()
    serializer_class = NeighborhoodSerializer
    pagination_class = OptionalLimitOffsetPagination
    permission_classes = (IsAdminOrgAndAdminCreateEditOnly,)
    filter_fields = ('organization', 'name', 'label', 'state_abbrev')
    filter_backends = (DjangoFilterBackend, OrderingFilter, OrgAutoFilterBackend)
    ordering_fields = ('created_at',)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(organization=self.request.user.organization,
                            name=slugify(serializer.validated_data['label']))


class USStateView(APIView):
    """Convenience endpoint for available U.S. state options."""

    def get(self, request, format=None):
        return Response([{'abbr': state.abbr, 'name': state.name} for state in us.STATES])
