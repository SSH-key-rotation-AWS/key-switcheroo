from abc import ABC, abstractmethod
from pathlib import Path
from switcheroo.ssh.objects import Key, KeyMetadata
from switcheroo.ssh.data_stores import ssh_home_file_ds
from switcheroo import paths
from switcheroo.ssh.metric_constants import Constants
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

    def _publish_metrics(self, metric_publisher: MetricPublisher):
        time_metric = TimingMetric(Constants.TIMING_METRIC_NAME, "None")
        counter_metric = CounterMetric(Constants.COUNTER_METRIC_NAME, "Count")
        metric_publisher.publish_metric(time_metric)
        metric_publisher.publish_metric(counter_metric)

    def publish_key(
        self,
        host: str,
        user: str,
        key: Key | None = None,
        metadata: KeyMetadata | None = None,
        metric_publisher: MetricPublisher | None = None
    ) -> tuple[Key, KeyMetadata]:
        # Lazy evaluation of default values
        if key is None:
            key = Key()
        if metadata is None:
            metadata = KeyMetadata.now_by_executing_user()
        self._publish_public_key(key.public_key, host, user)
        self._publish_private_key(key.private_key, host, user)
        self._publish_key_metadata(metadata, host, user)
        if metric_publisher is not None:
            self._publish_metrics(metric_publisher)
        return (key, metadata)


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
