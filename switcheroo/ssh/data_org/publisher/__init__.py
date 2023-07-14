from abc import ABC, abstractmethod
from pathlib import Path
from switcheroo.ssh.objects import Key, KeyMetadata
from switcheroo.ssh.data_stores import ssh_home_file_ds
from switcheroo import paths
from switcheroo.ssh import MetricConstants
from metric_system.functions.metric_publisher import MetricPublisher
from metric_system.functions.metrics import CounterMetric, TimingMetric


class KeyPublisher(ABC):
    @abstractmethod
    def _publish_public_key(self, key: Key.PublicComponent, host: str, user: str):
        pass

    @abstractmethod
    def _publish_private_key(self, key: Key.PrivateComponent, host: str, user: str):
        pass

    @abstractmethod
    def _publish_key_metadata(self, metadata: KeyMetadata, host: str, user: str):
        pass

    def _publish_metrics(
        self, metric_publisher: MetricPublisher, timing_metric: TimingMetric
    ):
        """Creates counter metric and publishes it with the metric_publisher passed in.
        Takes in the timing metric, whose value is the time it took to publish the keys,
        and publishes the metric"""
        counter_metric = CounterMetric(MetricConstants.COUNTER_METRIC_NAME, "Count")
        counter_metric.increment()
        metric_publisher.publish_metric(timing_metric)
        metric_publisher.publish_metric(counter_metric)

    def _publish_keys_and_metadata(
        self,
        host: str,
        user: str,
        key: Key | None = None,
        metadata: KeyMetadata | None = None,
    ) -> tuple[Key, KeyMetadata]:
        "Helper function for publishing keys and metadata"
        # Lazy evaluation of default values
        if key is None:
            key = Key()
        if metadata is None:
            metadata = KeyMetadata.now_by_executing_user()
        self._publish_public_key(key.public_key, host, user)
        self._publish_private_key(key.private_key, host, user)
        self._publish_key_metadata(metadata, host, user)
        return (key, metadata)

    def publish_key(
        self,
        host: str,
        user: str,
        key: Key | None = None,
        metadata: KeyMetadata | None = None,
        metric_publisher: MetricPublisher | None = None,
    ) -> tuple[Key, KeyMetadata]:
        """
        Public method for publishing keys and key metadata,
        as well as metrics if selected by the user.

        Args:
            host (str, required): the hostname of the server
            user (str, required): the username of the connecting client
            key (Key, optional): Key object. Defaults to None
            metadata(KeyMetadata, optional): KeyMetadata object. Defaults to None
            metric_publisher (MetricPublisher, optional): MetricPublisher object. Defaults to None

        Returns:
            A tuple with the Key and KeyMetadata
        """
        if metric_publisher is not None:  # the user decided to publish metrics
            timing_metric = TimingMetric(MetricConstants.TIMING_METRIC_NAME, "None")
            key_and_metadata: tuple[Key, KeyMetadata] | None = None
            # use the timeit() context manager to time how long it takes to publish new keys
            with timing_metric.timeit():
                key_and_metadata = self._publish_keys_and_metadata(
                    host, user, key, metadata
                )
            self._publish_metrics(
                metric_publisher, timing_metric
            )  # publish the metrics
            return key_and_metadata
        # if the user decided not to publish metrics just publish the keys and their metadata
        return self._publish_keys_and_metadata(host, user, key, metadata)


class FileKeyPublisher(KeyPublisher):
    def __init__(self, ssh_home: Path = paths.local_ssh_home()):
        self._ssh_home = ssh_home
        self._key_ds = ssh_home_file_ds(ssh_home)

    def _publish_public_key(self, key: Key.PublicComponent, host: str, user: str):
        return self._key_ds.publish(
            item=key, location=paths.local_relative_public_key_loc(host, user)
        )

    def _publish_private_key(self, key: Key.PrivateComponent, host: str, user: str):
        return self._key_ds.publish(
            item=key, location=paths.local_relative_private_key_loc(host, user)
        )

    def _publish_key_metadata(self, metadata: KeyMetadata, host: str, user: str):
        return self._key_ds.publish(
            item=metadata, location=paths.local_relative_metadata_loc(host, user)
        )
